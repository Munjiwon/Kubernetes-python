#!/usr/bin/env python3
"""
Process State Analyzer
프로세스 상태를 분석하고 리포트를 생성하는 도구
"""

import subprocess
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
import argparse
import os

class ProcessAnalyzer:
    def __init__(self, namespace="gc-simulator"):
        self.namespace = namespace
        self.data_history = []
        
    def collect_metrics(self, duration_minutes=5, interval_seconds=10):
        """지정된 시간 동안 메트릭 수집"""
        print(f"Collecting metrics for {duration_minutes} minutes...")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            metrics = self.get_current_metrics()
            if metrics:
                self.data_history.append(metrics)
                print(f"Collected data point {len(self.data_history)}")
            
            time.sleep(interval_seconds)
        
        print(f"Collection complete. Total data points: {len(self.data_history)}")
        return self.data_history
    
    def get_current_metrics(self):
        """현재 메트릭 수집"""
        timestamp = datetime.now()
        metrics = {
            'timestamp': timestamp.isoformat(),
            'pods': []
        }
        
        # Pod 목록 가져오기
        cmd = f"kubectl get pods -n {self.namespace} -o json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None
        
        pods = json.loads(result.stdout).get('items', [])
        
        for pod in pods:
            pod_name = pod['metadata']['name']
            pod_metrics = self.get_pod_details(pod_name)
            
            if pod_metrics:
                metrics['pods'].append(pod_metrics)
        
        return metrics
    
    def get_pod_details(self, pod_name):
        """Pod 상세 정보 수집"""
        details = {
            'name': pod_name,
            'processes': [],
            'resource_usage': {}
        }
        
        # 프로세스 정보
        cmd = f"kubectl exec -n {self.namespace} {pod_name} -- ps aux"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                parts = line.split(None, 10)
                if len(parts) >= 11 and 'python' in parts[10]:
                    details['processes'].append({
                        'pid': parts[1],
                        'cpu': float(parts[2]),
                        'mem': float(parts[3]),
                        'command': parts[10]
                    })
        
        # 리소스 사용량
        cmd = f"kubectl exec -n {self.namespace} {pod_name} -- cat /proc/meminfo"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'MemTotal:' in line:
                    details['resource_usage']['mem_total'] = int(line.split()[1])
                elif 'MemAvailable:' in line:
                    details['resource_usage']['mem_available'] = int(line.split()[1])
        
        return details
    
    def analyze_data(self):
        """수집된 데이터 분석"""
        if not self.data_history:
            print("No data to analyze")
            return None
        
        analysis = {
            'summary': {},
            'by_pod': {},
            'by_state': {},
            'trends': {}
        }
        
        # Pod별 분석
        all_pods = {}
        for data_point in self.data_history:
            for pod in data_point['pods']:
                pod_name = pod['name']
                if pod_name not in all_pods:
                    all_pods[pod_name] = {
                        'cpu_values': [],
                        'mem_values': [],
                        'process_counts': []
                    }
                
                # CPU 평균
                cpu_avg = np.mean([p['cpu'] for p in pod['processes']]) if pod['processes'] else 0
                all_pods[pod_name]['cpu_values'].append(cpu_avg)
                
                # 메모리 평균
                mem_avg = np.mean([p['mem'] for p in pod['processes']]) if pod['processes'] else 0
                all_pods[pod_name]['mem_values'].append(mem_avg)
                
                # 프로세스 수
                all_pods[pod_name]['process_counts'].append(len(pod['processes']))
        
        # Pod별 통계
        for pod_name, data in all_pods.items():
            analysis['by_pod'][pod_name] = {
                'cpu': {
                    'mean': np.mean(data['cpu_values']),
                    'std': np.std(data['cpu_values']),
                    'max': np.max(data['cpu_values']),
                    'min': np.min(data['cpu_values'])
                },
                'memory': {
                    'mean': np.mean(data['mem_values']),
                    'std': np.std(data['mem_values']),
                    'max': np.max(data['mem_values']),
                    'min': np.min(data['mem_values'])
                },
                'processes': {
                    'mean': np.mean(data['process_counts']),
                    'total': np.sum(data['process_counts'])
                }
            }
        
        # 프로세스 상태별 분류
        for pod_name in all_pods:
            cpu_mean = analysis['by_pod'][pod_name]['cpu']['mean']
            
            if cpu_mean > 70:
                state = 'foreground_active'
            elif cpu_mean > 40:
                state = 'active'
            elif cpu_mean > 20:
                state = 'background_active'
            elif cpu_mean > 5:
                state = 'running'
            else:
                state = 'inactive'
            
            if state not in analysis['by_state']:
                analysis['by_state'][state] = []
            
            analysis['by_state'][state].append(pod_name)
        
        # 전체 요약
        all_cpu = []
        all_mem = []
        for data in all_pods.values():
            all_cpu.extend(data['cpu_values'])
            all_mem.extend(data['mem_values'])
        
        analysis['summary'] = {
            'total_pods': len(all_pods),
            'avg_cpu': np.mean(all_cpu) if all_cpu else 0,
            'avg_memory': np.mean(all_mem) if all_mem else 0,
            'data_points': len(self.data_history)
        }
        
        return analysis
    
    def generate_report(self, analysis, output_dir="reports"):
        """분석 리포트 생성"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 텍스트 리포트
        report_file = os.path.join(output_dir, f"analysis_report_{timestamp}.txt")
        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("Process State Analysis Report\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("=" * 80 + "\n\n")
            
            # 요약
            f.write("SUMMARY\n")
            f.write("-" * 40 + "\n")
            for key, value in analysis['summary'].items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # 상태별 분류
            f.write("PODS BY STATE\n")
            f.write("-" * 40 + "\n")
            for state, pods in analysis['by_state'].items():
                f.write(f"{state}: {len(pods)} pods\n")
                for pod in pods:
                    f.write(f"  - {pod}\n")
            f.write("\n")
            
            # Pod별 상세
            f.write("POD DETAILS\n")
            f.write("-" * 40 + "\n")
            for pod_name, data in analysis['by_pod'].items():
                f.write(f"\n{pod_name}:\n")
                f.write(f"  CPU: mean={data['cpu']['mean']:.2f}%, "
                       f"max={data['cpu']['max']:.2f}%, "
                       f"std={data['cpu']['std']:.2f}\n")
                f.write(f"  Memory: mean={data['memory']['mean']:.2f}%, "
                       f"max={data['memory']['max']:.2f}%\n")
                f.write(f"  Processes: {data['processes']['mean']:.1f}\n")
        
        print(f"Report saved to: {report_file}")
        
        # JSON 리포트
        json_file = os.path.join(output_dir, f"analysis_data_{timestamp}.json")
        with open(json_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"JSON data saved to: {json_file}")
        
        return report_file
    
    def visualize_data(self, analysis, output_dir="reports"):
        """데이터 시각화"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Figure 설정
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Process State Analysis', fontsize=16)
        
        # 1. Pod별 CPU 사용률
        pod_names = list(analysis['by_pod'].keys())
        cpu_means = [analysis['by_pod'][pod]['cpu']['mean'] for pod in pod_names]
        
        axes[0, 0].bar(range(len(pod_names)), cpu_means)
        axes[0, 0].set_title('Average CPU Usage by Pod')
        axes[0, 0].set_xlabel('Pod')
        axes[0, 0].set_ylabel('CPU %')
        axes[0, 0].set_xticks(range(len(pod_names)))
        axes[0, 0].set_xticklabels([p.split('-')[0] for p in pod_names], rotation=45)
        
        # 2. Pod별 메모리 사용률
        mem_means = [analysis['by_pod'][pod]['memory']['mean'] for pod in pod_names]
        
        axes[0, 1].bar(range(len(pod_names)), mem_means, color='orange')
        axes[0, 1].set_title('Average Memory Usage by Pod')
        axes[0, 1].set_xlabel('Pod')
        axes[0, 1].set_ylabel('Memory %')
        axes[0, 1].set_xticks(range(len(pod_names)))
        axes[0, 1].set_xticklabels([p.split('-')[0] for p in pod_names], rotation=45)
        
        # 3. 상태별 Pod 분포
        states = list(analysis['by_state'].keys())
        state_counts = [len(analysis['by_state'][state]) for state in states]
        
        axes[1, 0].pie(state_counts, labels=states, autopct='%1.1f%%')
        axes[1, 0].set_title('Pod Distribution by State')
        
        # 4. CPU vs Memory 산점도
        cpu_all = []
        mem_all = []
        for pod in analysis['by_pod'].values():
            cpu_all.append(pod['cpu']['mean'])
            mem_all.append(pod['memory']['mean'])
        
        axes[1, 1].scatter(cpu_all, mem_all, s=100, alpha=0.6)
        axes[1, 1].set_title('CPU vs Memory Usage')
        axes[1, 1].set_xlabel('CPU %')
        axes[1, 1].set_ylabel('Memory %')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 상태별 영역 표시
        axes[1, 1].axvline(x=70, color='r', linestyle='--', alpha=0.3, label='Foreground')
        axes[1, 1].axvline(x=40, color='y', linestyle='--', alpha=0.3, label='Active')
        axes[1, 1].axvline(x=20, color='g', linestyle='--', alpha=0.3, label='Background')
        axes[1, 1].axvline(x=5, color='b', linestyle='--', alpha=0.3, label='Running')
        axes[1, 1].legend()
        
        plt.tight_layout()
        
        # 저장
        plot_file = os.path.join(output_dir, f"analysis_plot_{timestamp}.png")
        plt.savefig(plot_file, dpi=100, bbox_inches='tight')
        plt.close()
        
        print(f"Visualization saved to: {plot_file}")
        
        return plot_file

def main():
    parser = argparse.ArgumentParser(description='Process State Analyzer')
    parser.add_argument('-n', '--namespace', default='process-experiments',
                        help='Kubernetes namespace')
    parser.add_argument('-d', '--duration', type=int, default=5,
                        help='Collection duration in minutes')
    parser.add_argument('-i', '--interval', type=int, default=10,
                        help='Collection interval in seconds')
    parser.add_argument('--analyze-only', action='store_true',
                        help='Analyze existing data only')
    parser.add_argument('--data-file', type=str,
                        help='Path to existing data file for analysis')
    
    args = parser.parse_args()
    
    analyzer = ProcessAnalyzer(namespace=args.namespace)
    
    if args.analyze_only and args.data_file:
        # 기존 데이터 로드
        with open(args.data_file, 'r') as f:
            analyzer.data_history = json.load(f)
    else:
        # 새 데이터 수집
        analyzer.collect_metrics(
            duration_minutes=args.duration,
            interval_seconds=args.interval
        )
    
    # 분석 수행
    analysis = analyzer.analyze_data()
    
    if analysis:
        # 리포트 생성
        analyzer.generate_report(analysis)
        
        # 시각화
        try:
            import matplotlib
            analyzer.visualize_data(analysis)
        except ImportError:
            print("Matplotlib not installed. Skipping visualization.")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    import time
    main()
