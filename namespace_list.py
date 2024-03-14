'''
from kubernetes import client, config, watch
# Configs can be set in Configuration class directly or using helper utility
#간단한 네임스페이스 10개 출력
config.load_kube_config()

v1 = client.CoreV1Api()
count = 10
w = watch.Watch()
for event in w.stream(v1.list_namespace, _request_timeout=60):
    print("Event: %s %s" % (event['type'], event['object'].metadata.name))
    count -= 1
    if not count:
        w.stop()

print("Ended.")
'''

'''
Uses watch to print the stream of events from list namespaces and list pods.
The script will wait for 10 events related to namespaces to occur within
the `timeout_seconds` threshold and then move on to wait for another 10 events
related to pods to occur within the `timeout_seconds` threshold.
watch를 사용하여 목록 네임스페이스 및 목록 Pod에서 이벤트 스트림을 인쇄합니다.
스크립트는 네임스페이스와 관련된 10개의 이벤트가 발생할 때까지 기다립니다.
`timeout_seconds` 임계값을 초과한 다음 계속해서 다른 10개의 이벤트를 기다립니다.
'timeout_seconds' 임계값 내에 발생하는 포드와 관련됩니다.
'''

from kubernetes import client, config, watch


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    v1 = client.CoreV1Api()
    count = 10
    w = watch.Watch()
    for event in w.stream(v1.list_namespace, timeout_seconds=10):
        print("Event: %s %s" % (event['type'], event['object'].metadata.name))
        count -= 1
        if not count:
            w.stop()
    print("Finished namespace stream.")

    for event in w.stream(v1.list_pod_for_all_namespaces, timeout_seconds=10):
        print("Event: %s %s %s" % (
            event['type'],
            event['object'].kind,
            event['object'].metadata.name)
        )
        count -= 1
        if not count:
            w.stop()
    print("Finished pod stream.") #pod만 출력


if __name__ == '__main__':
    main()