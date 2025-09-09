#!/usr/bin/env python3
"""
Process Monitoring Tool
프로세스 시뮬레이터의 상태를 모니터링하고 분석하는 도구
"""

import subprocess
import json
import time
import argparse
from datetime import datetime
from collections import defaultdict
import sys

class ProcessMonitor:
    def __init__(self, namespace="process-experiments"):
        self.namespace = namespace
        self.process_states = {}
        self.resource_usage = {}
        
    def get_pods(self):
        """네임스페이스의 모든 Pod 가져오기"""
        cmd = f"kubectl get pods -n {self.namespace} -o json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting pods: {result.stderr}")
            return []
        
        data = json.loads(result.stdout)
        return data.get('items', [])
    
    def get_pod_processes(self, pod_name):
        """Pod 내부 프로세스 정보 가져오기"""
        cmd = f"kubectl exec -n {self.namespace} {pod_name} -- ps aux"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None
        
        lines = result.stdout.strip().split('\n')
        processes = []
        
        for line in lines[1:]:  # Skip header
            parts = line.split(None, 10)
            if len(parts) >= 11:
                processes.append({
                    'user': parts[0],
                    'pid': parts[1],
                    'cpu': float(parts[2]),
                    'mem': float(parts[3]),
                    'vsz': parts[4],
                    'rss': parts[5],
                    'tty': parts[6],
                    'stat': parts[7],
                    'start': parts[8],
                    'time': parts[9],
                    'command': parts[10]
                })
        
        return processes
    
    def get_pod_metrics(self, pod_name):
        """Pod 리소스 메트릭 가져오기"""
        cmd = f"kubectl top pod {pod_name} -n {self.namespace} --no-headers"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None
        
        parts = result.stdout.strip().split()
        if len(parts) >= 3:
            return {
                'cpu': parts[1],
                'memory': parts[2]
            }
        return None
    
    def analyze_process_state(self, processes):
        """프로세스 상태 분석"""
        if not processes:
            return "unknown"
        
        python_processes = [p for p in processes if 'python' in p['command']]
        
        total_cpu = sum(p['cpu'] for p in python_processes)
        avg_cpu = total_cpu / len(python_processes) if python_processes else 0
        
        # 상태 판단
        if avg_cpu > 70:
            return "foreground_active"
        elif avg_cpu > 40:
            return "active"
        elif avg_cpu > 20:
            return "background_active"
        elif avg_cpu > 5:
            return "running"
        else:
            return "inactive"
    
    def monitor_loop(self, interval=5):
        """실시간 모니터링 루프"""
        print(f"Starting monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.clear_screen()
                self.print_header()
                
                pods = self.get_pods()
                
                if not pods:
                    print("No pods found in namespace")
                    time.sleep(interval)
                    continue
                
                # Pod 정보 수집
                pod_data = []
                for pod in pods:
                    name = pod['metadata']['name']
                    status = pod['status']['phase']
                    
                    # 프로세스 정보
                    processes = self.get_pod_processes(name)
                    process_count = len(processes) if processes else 0
                    
                    # 메트릭 정보
                    metrics = self.get_pod_metrics(name)
                    
                    # 상태 분석
                    state = self.analyze_process_state(processes) if processes else "unknown"
                    
                    pod_data.append({
                        'name': name,
                        'status': status,
                        'processes': process_count,
                        'state': state,
                        'metrics': metrics
                    })
                
                # 테이블 출력
                self.print_pod_table(pod_data)
                
                # 통계 출력
                self.print_statistics(pod_data)
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
    
    def clear_screen(self):
        """화면 지우기"""
        subprocess.run('clear' if sys.platform != 'win32' else 'cls', shell=True)
    
    def print_header(self):
        """헤더 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("=" * 80)
        print(f"Process Simulator Monitor - {timestamp}")
        print("=" * 80)
    
    def print_pod_table(self, pod_data):
        """Pod 정보 테이블 출력"""
        print("\nPod Status:")
        print("-" * 80)
        print(f"{'Pod Name':<30} {'Status':<10} {'Procs':<8} {'State':<20} {'CPU':<10} {'Memory':<10}")
        print("-" * 80)
        
        for pod in pod_data:
            cpu = pod['metrics']['cpu'] if pod['metrics'] else 'N/A'
            mem = pod['metrics']['memory'] if pod['metrics'] else 'N/A'
            
            print(f"{pod['name']:<30} {pod['status']:<10} {pod['processes']:<8} "
                  f"{pod['state']:<20} {cpu:<10} {mem:<10}")
    
    def print_statistics(self, pod_data):
        """통계 정보 출력"""
        print("\n" + "-" * 80)
        print("Statistics:")
        
        # 상태별 Pod 수
        state_counts = defaultdict(int)
        for pod in pod_data:
            state_counts[pod['state']] += 1
        
        print("\nPods by State:")
        for state, count in sorted(state_counts.items()):
            print(f"  {state:<20}: {count}")
        
        # 총 프로세스 수
        total_processes = sum(pod['processes'] for pod in pod_data)
        print(f"\nTotal Processes: {total_processes}")
        print(f"Total Pods: {len(pod_data)}")
    
    def export_data(self, filename="monitor_data.json"):
        """모니터링 데이터 내보내기"""
        pods = self.get_pods()
        data = {
            'timestamp': datetime.now().isoformat(),
            'namespace': self.namespace,
            'pods': []
        }
        
        for pod in pods:
            name = pod['metadata']['name']
            processes = self.get_pod_processes(name)
            metrics = self.get_pod_metrics(name)
            
            data['pods'].append({
                'name': name,
                'status': pod['status']['phase'],
                'processes': processes,
                'metrics': metrics
            })
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"Data exported to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Process Simulator Monitor')
    parser.add_argument('-n', '--namespace', default='process-experiments',
                        help='Kubernetes namespace')
    parser.add_argument('-i', '--interval', type=int, default=5,
                        help='Monitoring interval in seconds')
    parser.add_argument('-e', '--export', action='store_true',
                        help='Export monitoring data to file')
    
    args = parser.parse_args()
    
    monitor = ProcessMonitor(namespace=args.namespace)
    
    if args.export:
        monitor.export_data()
    else:
        monitor.monitor_loop(interval=args.interval)

if __name__ == "__main__":
    main()
