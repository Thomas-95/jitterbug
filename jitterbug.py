import ast
import os


def jitterbug():
    # to_parse = 'x = 1\ny = 2\nz= x + y'  # TODO: Add support for this kind of assignment
    to_parse = 'def get_one():\n    return 1'

    print ('Generating C++ code from Python source...')

    # jitterbug supports only a handful of the Python ast node classes.
    # For a more comprehensive list of nodes within the Python ast:
    # https://greentreesnakes.readthedocs.io/en/latest/nodes.html
    code_generator = CCCodeGenerator()
    code_generator.visit(ast.parse(to_parse))
    print ('\nCCCodeGenerator output: \n' + code_generator.cc_code)

    cc_code = ('#include <iostream>\n int main() { %s return 0;}' % code_generator.cc_code)

    print ('Successfully generated code!')

    return cc_code


class CCCodeGenerator(ast.NodeVisitor):
    cc_code = ''

    def visit_Expr(self, node):
        """
        When an expression, such as a function call, appears as a statement by
        itself (an expression statement), with its return value not used or
        stored, it is wrapped in this container.
        """
        self.visit(node.value)
        self.cc_code += ';'

    def visit_Assign(self, node):
        if node.value.__class__ == ast.Num:
            if type(node.value.n) == int:
                self.cc_code += 'int '
            else:
                self.cc_code += 'double '
        elif node.value.__class__ == ast.Str:
            self.cc_code += 'std::string '
        elif node.value.__class__ == ast.BinOp:
            if node.value.left.__class__ == ast.Name:
                raise TypeError('Jitterbug does not currently support statements of the kind "z = x + y".')

        if len(node.targets) != 1:
            raise ValueError('Jitterbug expects the "targets" attribute to have length 1.\
                              It does not currently support tuple unpacking.')

        self.visit(node.targets[0])
        self.visit(node.value)
        self.cc_code += ';\n'

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.op)
        self.visit(node.right)

    def visit_Add(self, node):
        self.cc_code += '+'

    def visit_Sub(self, node):
        self.cc_code += '-'

    def visit_Mult(self, node):
        self.cc_code += '*'

    def visit_Div(self, node):
        self.cc_code += '/'

    def visit_Mod(self, node):
        self.cc_code += '**'

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.cc_code += node.id
            self.cc_code += ' = '
        elif isinstance(node.ctx, ast.Load):
            self.cc_code += node.id

    def visit_Num(self, node):
        self.cc_code += str(node.n)

    # def visit_Store(self, node):
    #     self.cc_code += ' = '

    def visit_Str(self, node):
        self.cc_code += '"%s"' % node.s

    def visit_Compare(self, node):
        self.visit(node.left)

        if len(node.ops) > 1:
            raise SyntaxError('Jitterbug only supports single operations in comparison expressions. You supplied {}.'.format(len(node.ops)))

        operator = node.ops[0]

        if isinstance(operator, ast.Eq):
            self.cc_code += ' == '
        elif isinstance(operator, ast.NotEq):
            self.cc_code += ' != '
        elif isinstance(operator, ast.Lt):
            self.cc_code += ' < '
        elif isinstance(operator, ast.LtE):
            self.cc_code += ' <= '
        elif isinstance(operator, ast.Gt):
            self.cc_code += ' > '
        elif isinstance(operator, ast.GtE):
            self.cc_code += ' >= '
        elif node.__class__ in [ast.Is, ast.IsNot, ast.In, ast.NotIn]:
            raise TypeError('Jitterbug does not currently support the {} syntax.'.format(node.ops))
        else:
            raise TypeError('Jitterbug does not recognise the operator {}.'.format(node.ops))

        print (node.comparators)

        if len(node.comparators) > 1:
            raise SyntaxError('Jitterbug only supports single comparators in comparison expressions. You supplied {}.'.format(len(node.comparators)))

        self.visit(node.comparators[0])

    def visit_If(self, node):
        self.cc_code += "if ("
        self.visit(node.test)
        self.cc_code += ')'

        self.cc_code += '{'

        for n in node.body:
            self.visit(n)

        self.cc_code += '}'

    def visit_FunctionDef(self, node):
        self.cc_code += 'int '
        self.cc_code += node.name
        self.cc_code += '() '
        if len(node.args.args) != 0:
            raise TypeError('jitterbug does not currently support passing arguments to functions.')
        self.cc_code += '{'
        for node in node.body[:-1]:
            self.visit(node)
        self.cc_code += 'return '
        self.visit(node.body[-1])
        self.cc_code += '}'
        self.cc_code += ';'


def cc_write(cc_code, filename='output.cc'):
    print ('Writing C++ code to {} ...'.format(filename))
    with open(filename, 'w') as output:
        output.write(cc_code)
    print ('Successfully written to file!')
    return None


def cc_compile(filename='output.cc'):
    print ('Compiling generated C++ from source {} ... \n'.format(filename))
    os.system('g++ --std=c++11 {} -o {}'.format(filename, filename.split('.')[0]))
    print ('Successfully compiled C++ code from Python source!')


def cc_execute(filename='output.cc'):
    filename_no_extension = filename.split('.')[0]
    print ('Executing compiled C++ code containted in {}'.format(filename_no_extension))
    os.system('./{}'.format(filename_no_extension))
    print ('Successfully executed C++ code contained in {} !'.format(filename_no_extension))


if __name__ == '__main__':
    cc = jitterbug()
    cc_write(cc)
    cc_compile()
    cc_execute()
