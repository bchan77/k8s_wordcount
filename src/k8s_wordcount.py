import logging
from kubernetes import client, config
import getopt, sys



def create_pvc_if_not_exist():
    print("create_pvc_if_not_exist")


def print_usage():
    print(sys.argv[0] +  "-h " \
                         "--LOG <DEBUG|INFO|WARNING|ERROR|CRITICAL>"
          )


def main():
    LOGGING=logging.INFO # By default, just log info

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["--log="])

    except getopt.GetoptError:
        print_usage()
        sys.exit(-1)

    for opt,arg in opts:
        if opt.upper() == ("--LOG"):
            if(arg.upper() not in ['DEBUG', "INFO", "WARNING", "ERROR","CRITICAL"]):
                print("ERROR: --Log needs to be in DEBUG, INFO, WARNING, ERROR or CRITICAL ")
                print_usage()


if __name__ == "__main__":
    main()
