import ast
import os


# TODO make the function below a smarter, recursive function.
def jitterbug():
    parsed_assignment = (ast.parse('x = 5'))

    cc_code = ['#include <iostream> \n']

    print ('Generating C++ code from Python source...')

    # jitterbug supports only a handful of the Python ast node classes.
    # For a more comprehensive list of nodes within the Python ast:
    # https://greentreesnakes.readthedocs.io/en/latest/nodes.html
    for node in ast.walk(parsed_assignment):
        print (node.__class__)

        if isinstance(node, (ast.Module, ast.Expr,)):
            continue

        elif isinstance(node, ast.Assign):
            cc_code.append('int ')

        elif isinstance(node, ast.Store):
            continue

        elif isinstance(node, ast.Num):
            cc_code.append(str(node.n))

        elif isinstance(node, ast.Name):
            cc_code.append(node.id)
            if isinstance(node.ctx, ast.Store):
                cc_code.append(' = ')

        else:
            raise TypeError('Type {} is not yet supported by jitterbug.'.format(node))

    cc_code.append(';\n')
    cc_code.append('int main() {return 0;}')

    cc_code = ''.join(cc_code)

    print ('Successfully generated code!')

    return cc_code


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
