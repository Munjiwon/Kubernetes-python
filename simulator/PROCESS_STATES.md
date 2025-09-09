# Process State Configuration

## Process State Definitions

### Foreground Active
- **특징**: 사용자와 상호작용하며 활발히 작동
- **CPU 사용률**: 80-95%
- **메모리 패턴**: 점진적 증가
- **I/O 활동**: 빈번한 stdout 출력
- **예시**: 데이터 처리 UI, 실시간 모니터링

### Background Active  
- **특징**: 백그라운드에서 지속적 작업
- **CPU 사용률**: 50-70%
- **메모리 패턴**: 안정적
- **I/O 활동**: 파일 로깅
- **예시**: 워커 프로세스, 캐시 서비스

### Active
- **특징**: 버스트 모드로 활동
- **CPU 사용률**: 변동적 (0-90%)
- **메모리 패턴**: 버스트시 증가
- **I/O 활동**: 간헐적
- **예시**: 배치 작업, 정기 태스크

### Running
- **특징**: 일정한 속도로 지속 실행
- **CPU 사용률**: 30-50%
- **메모리 패턴**: 일정
- **I/O 활동**: 규칙적
- **예시**: 이벤트 루프, 큐 처리

### Inactive
- **특징**: 대부분 유휴 상태
- **CPU 사용률**: <5%
- **메모리 패턴**: 최소
- **I/O 활동**: 거의 없음
- **예시**: 대기 프로세스, 슬립 상태

## 프로세스 동작 패턴

```python
# Foreground Active 패턴
while True:
    heavy_computation()
    print(f"Status: {status}")  # 자주 출력
    time.sleep(0.001)

# Background Active 패턴
while True:
    process_task()
    if count % 1000 == 0:
        log_to_file(status)  # 파일로만 로깅
    time.sleep(0.01)

# Active (Burst) 패턴
while True:
    # 활동 기간
    for _ in range(burst_duration):
        intensive_work()
    # 휴식 기간
    time.sleep(idle_duration)

# Running 패턴
while True:
    task = get_next_task()
    process(task)
    time.sleep(0.1)  # 일정한 속도

# Inactive 패턴
while True:
    time.sleep(30)  # 긴 대기
    if check_condition():
        minimal_work()
```

## 리소스 프로파일

| State | CPU (%) | Memory (MB) | Threads | I/O Ops/sec |
|-------|---------|-------------|---------|-------------|
| Foreground Active | 80-95 | 50-200 | 1-2 | 100-500 |
| Background Active | 50-70 | 30-100 | 3-5 | 10-50 |
| Active | 40-90 | 20-150 | 2-4 | 5-100 |
| Running | 30-50 | 10-50 | 1-3 | 1-20 |
| Inactive | 0-5 | 5-20 | 1 | 0-1 |

## 사용 시나리오

### 1. 웹 서버 시뮬레이션
```yaml
containers:
  - name: web-frontend
    env:
      - name: PROCESS_STATE
        value: "foreground_active"
      - name: NUM_PROCS
        value: "2"
  - name: web-backend
    env:
      - name: PROCESS_STATE
        value: "background_active"
      - name: NUM_PROCS
        value: "4"
```

### 2. 데이터 파이프라인 시뮬레이션
```yaml
containers:
  - name: data-ingestion
    env:
      - name: PROCESS_STATE
        value: "running"
      - name: NUM_PROCS
        value: "2"
  - name: data-processing
    env:
      - name: PROCESS_STATE
        value: "active"
      - name: NUM_PROCS
        value: "3"
```

### 3. 마이크로서비스 시뮬레이션
```yaml
containers:
  - name: microservice-mix
    env:
      - name: PROCESS_MIX
        value: "diverse"
      - name: NUM_PROCS
        value: "10"
```

## 모니터링 메트릭

### CPU 메트릭
- User CPU Time
- System CPU Time  
- CPU Usage Percentage
- Context Switches

### 메모리 메트릭
- RSS (Resident Set Size)
- VSZ (Virtual Size)
- Heap Usage
- Stack Usage

### I/O 메트릭
- Read Operations
- Write Operations
- Network I/O
- File Descriptors

### 프로세스 메트릭
- Process State (R/S/D/Z/T)
- Thread Count
- Child Processes
- Process Priority

## 튜닝 가이드

### CPU 최적화
```bash
# CPU 제한 설정
resources:
  limits:
    cpu: "500m"  # 0.5 CPU
  requests:
    cpu: "250m"  # 0.25 CPU
```

### 메모리 최적화
```bash
# 메모리 제한 설정
resources:
  limits:
    memory: "512Mi"
  requests:
    memory: "256Mi"
```

### 프로세스 수 최적화
```bash
# 노드 리소스에 따라 조정
NUM_PROCS = min(CPU_CORES * 2, MAX_PROCS)
```
