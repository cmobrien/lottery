import sys
import csv

def string_to_list(s):
    l = s[1:-1]
    l2 = l.split(', ')
    return l2
def is_empty_row(row):
    """Check if a row has only empty strings."""
    return not any(map(lambda cell: cell.strip(), row))

def main():


if __name__ == '__main__':
    main()
    #function = sys.argv[1]
    #locals()[function]()