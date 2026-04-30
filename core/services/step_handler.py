import random

def http_handler(step):
    result_config = {}
    config_json = step.step_config or {}
    simulate_failure_rate = config_json.get('simulate_failure_rate', 0.1)
    min_latency = config_json.get('min_latency', 100)
    max_latency = config_json.get('max_latency', 1000)
    # status_codes
    failure_status_codes = [400, 500]

    # Status
    random_failure = round(random.random(), 2)
    print(random_failure)
    if random_failure<simulate_failure_rate:
        result_config['status'] = 'failed'
        result_config['output_characteristics'] = {
            'status_code' : random.choice(failure_status_codes)
        }
        if result_config['output_characteristics']['status_code'] == 400:
            result_config['retryable'] = False
        else:
            result_config['retryable'] = True
    else:
        result_config['status'] = 'success'
        result_config['retryable'] = False
        result_config['output_characteristics'] = {
            "status_code" : 200
        }
    # duration
    result_config['duration'] = random.randint(min_latency, max_latency)

    return result_config

def delay_handler(step):
    config_json = step.step_config or {}
    delay_ms = config_json.get('delay_ms', 100)
    return {
        "status": "success",
        "duration": delay_ms,
        "retryable": False,
        "output_characteristics": {}
    }

def step_handler(step):
    dispatch_mapping = {
        "http_call": http_handler, 
        "delay": delay_handler
    }
    step_type = step.step_type
    print(step_type)
    handler = dispatch_mapping.get(step_type)
    if not handler:
        return {
            "status": "failed",
            "duration": 0,
            "retryable": False,
            "output_characteristics": {
                "error": f"Unsupported step type: {step_type}"
            }
        }

    return handler(step)
