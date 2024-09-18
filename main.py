import email_finder
import file_sorter
import sys, os

def main():
    try:
        email_finder.main()
        file_sorter.main()
        input("Success!")
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print("Error!")
    
    
    
if __name__ == "__main__":
    main()