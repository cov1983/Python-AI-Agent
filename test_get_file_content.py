from functions.get_file_content import get_file_content

def test():

    print("Print the content of main.py:")
    print(get_file_content("calculator", "main.py"))

    print("Print the content of pkg/calculator.py:")
    print(get_file_content("calculator", "pkg/calculator.py"))

    print("Attempt to access /bin/cat:")
    print(get_file_content("calculator", "/bin/cat"))

    print("Attempt to access a non-existent file:")
    print(get_file_content("calculator", "pkg/does_not_exist.py"))
    

if __name__ == "__main__":
    test()