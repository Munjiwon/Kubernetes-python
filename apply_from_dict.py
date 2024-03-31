'''
쿠버네티스 클러스터에서 nginx Deployment를 생성하는 예제
'''

from kubernetes import client, config, utils
def main():
    config.load_kube_config() #현재 환경에서 사용가능한 kubeconfig파일을 사용하여 쿠버네티스 클러스터에 연결
    k8s_client = client.ApiClient() #쿠버네티스 클러스터와의 통신을 위한 클라이언트 생성
    # nginx deployment를 정의하는 딕셔너리
    example_dict = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'k8s-py-client-nginx',
            'namespace': 'python-prac'
        },
        'spec': {
            'selector': {
                'matchLabels': {
                    'app': 'nginx'
                }
            },
            'replicas': 1,
            'template': {
                'metadata': {
                    'labels': {
                        'app': 'nginx'
                    }
                },
                'spec': {
                    'containers': [{
                        'name': 'nginx',
                        'image': 'nginx:1.14.2',
                        'ports': [{
                            'containerPort': 80
                        }]
                    }]
                }}}}
    utils.create_from_dict(k8s_client, example_dict) #example_dict에 정의한 내용대로 클러스터에 새로운 오브젝트 생성

if __name__ == '__main__':
    main()