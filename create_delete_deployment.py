from os import path

import time

import yaml

from kubernetes import client, config


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    with open(path.join(path.dirname(__file__), "../examples/yaml_dir/nginx-deployment.yaml")) as f:
        dep = yaml.safe_load(f)
        k8s_apps_v1 = client.AppsV1Api()
        resp = k8s_apps_v1.create_namespaced_deployment(
            body=dep, namespace="python-prac")
        print(f"Deployment created. Status='{resp.metadata.name}'")

        time.sleep(10) # 생성되고 10초의 시간을 준 다음 삭제

        resp = k8s_apps_v1.delete_namespaced_deployment( # 이름을 지정했는데 지정하지않고 불러오는 방법을 찾아보도록 하기
            name="nginx-deployment", namespace="python-prac"
        )


if __name__ == '__main__':
    main()