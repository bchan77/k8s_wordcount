import logging
from kubernetes import client, config
from os import path
import getopt, sys, time

SLEEP_TIME = 5 # in sec

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
        logging.info("Not going to create any PVC")

    is_pvc_ready = False
    #Wait for PVC to be ready
    while not is_pvc_ready:
        pvcs = kube_client.list_namespaced_persistent_volume_claim(namespace=namespace,watch=False)

        for i in pvcs.items:
            time.sleep(1)
            if (i.metadata.name == pvc_name):
                logging.debug(pvc_name + "is " + i.status.phase)
                if(i.status.phase == 'Bound'):
                    logging.info(pvc_name + "is ready")
                    is_pvc_ready=True


def delete_pvc(kube_client, namespace='default', pvc_name="k8s-wordcount-pvc"):
    logging.info("Deleting PVC : " + pvc_name)
    kube_client.delete_namespaced_persistent_volume_claim(pvc_name,namespace)
    logging.info("Done Deleting VPC")

def manifest_with_sleep(name):
#Source: https://github.com/kubernetes-client/python/blob/master/kubernetes/e2e_test/test_client.py
    return {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': name
        },
        'spec': {
            'volumes':[{
               'name': 'workcount-storage',
                'persistentVolumeClaim': {'claimName': 'k8s-wordcount-pvc'}
            }],
            'containers':[{
                'name': name,
                'image': 'debian',
                "command": [
                    "sleep",
                    "infinity"
                ],
                'volumeMounts' : [{'mountPath': "/data", 'name': 'workcount-storage'}],
                'imagePullPolicy': 'IfNotPresent'
            }]
        }
    }


def create_dummy_pod(kube_client,namespace='default', pvc_name="k8s-wordcount-pvc", pod_name="k8s-wordcount-dummy-pod"):

    logging.info("Creating Dummy Pod to copy file")
    stat_time = ""
    end_time = ""
    #should create_namespaced_pod
    pod_manifest = manifest_with_sleep(pod_name)
    logging.debug("pod_manifest: " + str(pod_manifest))
    resp = ""

    try:
        start_time = time.time()
        logging.info("Creating dummy pod")
        resp = kube_client.create_namespaced_pod(body=pod_manifest, namespace=namespace)

        is_pod_ready = False

        while not is_pod_ready:
            time.sleep(SLEEP_TIME)

            pods = kube_client.list_namespaced_pod(namespace=namespace,watch=False)

            for i in pods.items:
                if(i.metadata.name == pod_name):
                    logging.debug(pod_name + " creating status " + i.status.phase)

                    if(i.status.phase == "Running"):
                        is_pod_ready = True


        end_time = time.time()
        logging.info("Done with creating dummy pod " + str(round(end_time-start_time,2)) + "sec")

    except client.rest.ApiException as err:
        print("Error :" + str(err))
        #return -1 as error
        return -1

    return 0


def print_usage():
    print(sys.argv[0] +  " -h " \
                         "--log <DEBUG|INFO|WARNING|ERROR|CRITICAL>" \
                         "--cleanup"
          )


def main():
    LOGGING=logging.INFO # By default, just log info
    NAMESPACE="default"
    PVC_NAME = "k8s-wordcount-pvc"
    CLEANUP = False # False by default

    try:
        opts, args = getopt.getopt(sys.argv[1:], "-h", ["log=","cleanup"])

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

        elif opt.upper() == "--CLEANUP":
            CLEANUP = True

        elif opt == "-h":
            print_usage()


    #Lets get the KUBECONFIG
    config.load_kube_config()
    kube_client = client.CoreV1Api()

    #Testing only
    pvcs = get_all_pvc(kube_client,NAMESPACE)

    #Creating PVC
    create_pvc_if_not_exist(kube_client,NAMESPACE,PVC_NAME)

    #Creating create_dummy_pod
    create_dummy_pod(kube_client,NAMESPACE)


    ######Clean up here######

    if(CLEANUP):
        #Deleting VPC
        logging.info("CLEANING UP")
        delete_pvc(kube_client,NAMESPACE,PVC_NAME)


if __name__ == "__main__":
    main()
