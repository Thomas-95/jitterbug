import ast
import os


def jitterbug():
    to_parse = [
        'x = 5',
        'x = 3.14159',
        'x = "My string"',
        '"Hello, world!"',
        '1 + 2',
        '9 - 7',
        '15 / 5',
        '6 * 3',
        # 'x = 1\ny = 2\nz= x + y'  # TODO: Add support for this kind of variable assignment.
    ]

    # cc_code = ['#include <iostream> \n']

    print ('Generating C++ code from Python source...')

    # jitterbug supports only a handful of the Python ast node classes.
    # For a more comprehensive list of nodes within the Python ast:
    # https://greentreesnakes.readthedocs.io/en/latest/nodes.html
    for p in to_parse:
        code_generator = CCCodeGenerator()
        code_generator.visit(ast.parse(p))
        print ('\nCCCodeGenerator output: \n' + code_generator.cc_code)

    cc_code = ('int main() { %s return 0;}' % code_generator.cc_code)

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
            self.cc_code += 'string '
        elif node.value.__class__ == ast.Name:
            raise TypeError('Jitterbug does not currently support ')

        if len(node.targets) != 1:
            raise ValueError('Jitterbug expects the "targets" attribute to have length 1.')
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

    # TODO: Define BoolOps and Comparison nodes.

    def visit_Name(self, node):
        self.cc_code += node.id
        if isinstance(node.ctx, ast.Store):
            self.cc_code += ' = '

    def visit_Num(self, node):
        self.cc_code += str(node.n)

    # def visit_Store(self, node):
    #     self.cc_code += ' = '

    def visit_Str(self, node):
        self.cc_code += '"%s"' % node.s


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
