# API Helper Functions for ESP32-WROVER Smart Home
# Standardizes API responses and error handling

import json
import picoweb
import gc

def json_response(resp, data, status="200"):
    """Send JSON response with proper headers"""
    try:
        yield from picoweb.start_response(resp, content_type="application/json", status=status)
        yield from resp.awrite(json.dumps(data))
    except Exception as e:
        print(f"JSON response error: {e}")
        yield from error_response(resp, "Response error")

def error_response(resp, message, status="500"):
    """Send error response"""
    try:
        data = {"error": message, "status": "error"}
        yield from picoweb.start_response(resp, content_type="application/json", status=status)
        yield from resp.awrite(json.dumps(data))
    except:
        pass

def success_response(resp, message="Operation completed", data=None):
    """Send success response"""
    response_data = {"status": "success", "message": message}
    if data:
        response_data.update(data)
    yield from json_response(resp, response_data)

def parse_json_body(req):
    """Parse JSON request body"""
    try:
        content_length = int(req.headers.get(b'Content-Length', 0))
        if content_length > 0:
            body = yield from req.reader.readexactly(content_length)
            return json.loads(body.decode())
        return {}
    except Exception as e:
        print(f"JSON parse error: {e}")
        return {}

def safe_api_call(func):
    """Decorator for safe API calls with memory cleanup"""
    def wrapper(req, resp):
        try:
            result = yield from func(req, resp)
            gc.collect()  # Cleanup memory after API call
            return result
        except OSError:
            # Network errors - fail silently
            pass
        except Exception as e:
            print(f"API error in {func.__name__}: {e}")
            yield from error_response(resp, f"API error: {str(e)}")
        finally:
            gc.collect()
    return wrapper

def get_module_status(module, name):
    """Get standardized module status"""
    if module:
        return {
            "available": True,
            "name": name,
            "status": "active"
        }
    else:
        return {
            "available": False,
            "name": name,
            "status": "unavailable",
            "error": f"{name} not initialized"
        } 