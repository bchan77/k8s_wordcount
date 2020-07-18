import logging
from kubernetes import client, config
from os import path
import getopt, sys, yaml

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

def create_pvc_if_not_exist(kube_client, namespace = "default", pvc_name="k8s-wordcount-pvc"):

    #Get a list of PVC and see the pvc is there
    pvc_list  = get_all_pvc(kube_client, namespace)
    logging.debug("pvc_list=" + str(pvc_list))

    #If the pvc doesn't exist, create it
    if(pvc_name not in pvc_list):
        logging.info("Creating PVC: " + pvc_name)
        kube_client.create_namespaced_persistent_volume_claim(
            namespace=namespace,
            body = client.V1PersistentVolumeClaim(
                api_version='v1',
                kind='PersistentVolumeClaim',
                metadata=client.V1ObjectMeta(
                    name= pvc_name,
                ),
                spec=client.V1PersistentVolumeClaimSpec(
                    access_modes=[
                        'ReadWriteMany'
                    ],
                    resources=client.V1ResourceRequirements(
                        requests={
                            'storage': '10Gi'
                        }
                    ),
                    storage_class_name='managed-nfs-storage', #Change it to any storageclass you have
                    volume_mode='Filesystem'
                )
            )
        )
    else:
        logging.info("No going to create any PVC")

    #Wait for PVC to be ready



def print_usage():
    print(sys.argv[0] +  " -h " \
                         "--log <DEBUG|INFO|WARNING|ERROR|CRITICAL>"
          )


def main():
    LOGGING=logging.INFO # By default, just log info
    NAMESPACE="default"
    PVC_NAME = "k8s-wordcount-pvc"

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
