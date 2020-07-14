import logging
from kubernetes import client, config
import getopt, sys

def get_namespace():
    #Get a list of namespace
    print("get_namespace")

def get_all_pvc(kube_client, namespace):
    #Return a list of pvc
    logging.debug("Getting A list of PVC")
    logging.debug("=====================")
    pvc_list = []

    pvcs = kube_client.list_namespaced_persistent_volume_claim(namespace, watch=False)

    for i in pvcs.items:
        pvc_list.append(str(i.metadata.name))

    return pvc_list

def create_pvc_if_not_exist(kube_client, namespace = "default", pvc_name="k8s_wordcount_pvc"):

    pvc_list  = get_all_pvc(kube_client, namespace)
    print("create_pvc_if_not_exist")


def print_usage():
    print(sys.argv[0] +  " -h " \
                         "--LOG <DEBUG|INFO|WARNING|ERROR|CRITICAL>" \
                         "--pvc <k8s_wordcount>"
          )


def main():
    LOGGING=logging.INFO # By default, just log info
    NAMESPACE=""
    PVC_NAME = "k8s_wordcount_pvc"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "-h", ["log="])

    except getopt.GetoptError as err:
        print(str(err))
        print_usage()
        sys.exit(-1)

    for opt,arg in opts:
        if opt.upper() == "--LOG":
            if arg.upper() == "DEBUG":
                logging.basicConfig(level=logging.DEBUG)
            elif arg.upper() == "INFO":
                logging.basicConfig(level=logging.INFO)
            elif arg.upper() == "WARNING":
                logging.basicConfig(level=logging.WARNING)
            elif arg.upper() == "ERROR":
                logging.basicConfig(level=logging.ERROR)
            elif arg.upper() == "CRITICAL":
                logging.basicConfig(level=logging.CRITICAL)
            else:
                print("ERROR: --log needs to be in DEBUG, INFO, WARNING, ERROR or CRITICAL ")
        elif opt == "--pvc":
            PVC_NAME = arg

        elif opt == "-h":
            print_usage()


    #Lets get the KUBECONFIG
    config.load_kube_config()
    kube_client = client.CoreV1Api()

    #Testing only
    pvcs = get_all_pvc(kube_client,NAMESPACE)

    #Creating PVC
    create_pvc_if_not_exist(kube_client,NAMESPACE,PVC_NAME)

    print(pvcs)



if __name__ == "__main__":
    main()
