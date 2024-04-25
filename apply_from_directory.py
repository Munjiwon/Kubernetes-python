'''
쿠버네티스 클러스터에 여러 리소스를 YAML 파일에서 읽어와 생성하는 예제
'''

from kubernetes import client, config, utils

def main():
    config.load_kube_config() #현재 환경에서 사용가능한 kubeconfig파일을 사용하여 쿠버네티스 클러스터에 연결
    k8s_client = client.ApiClient() #쿠버네티스 클러스터와의 통신을 위한 클라이언트 생성
    yaml_dir = './yaml/' #YAML 파일이 위치한 디렉토리를 지정
    utils.create_from_directory(k8s_client, yaml_dir,verbose=True)
    #지정된 디렉토리에서 YAML 파일을 읽어와서 쿠버네티스 클러스터에 리소스를 생성
    #verbose=True 는 생성과정이 상세하게 출력

if __name__ == "__main__":
    main()