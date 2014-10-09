import sys
from chalmers.program import Program

def main():
    name = sys.argv[1]
    prog = Program(name)
    prog.start_sync()

if __name__ == '__main__':
    main()
