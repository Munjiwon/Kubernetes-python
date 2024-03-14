from os import path

import yaml

from kubernetes import client, config


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config() #필수 config값 불러옴

    with open(path.join(path.dirname(__file__), "filename.yaml")) as f:
        dep = yaml.safe_load(f) #yaml 파일 불러와서 저장
        k8s_apps_v1 = client.AppsV1Api() #api version

        resp = k8s_apps_v1.create_namespaced_deployment( #지정한 네임스페이스에 생성
            body=dep, namespace="namespace name") #body = 정의해둔 yaml, namespace = 네임스페이스
        k8s_apps_v1.delete_namespaced_deployment(
            name=dep, namespace="python-prac"
        )

if __name__ == '__main__':
    main()