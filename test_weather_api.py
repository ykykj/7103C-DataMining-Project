"""
和风天气 API 测试脚本
用于验证 API 配置是否正确
"""

import os
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv()

print("=" * 60)
print("和风天气 API 配置测试")
print("=" * 60)

# 获取配置
api_config = os.getenv("WEATHER_API_KEY", "")
print(f"\n1. 读取环境变量:")
print(f"   WEATHER_API_KEY = {api_config}")

# 解析配置
if "qweatherapi.com" in api_config:
    if "," in api_config:
        api_host, api_key = api_config.split(",", 1)
        base_url = f"https://{api_host.strip()}/v7"
        api_key = api_key.strip()
        print(f"\n2. 解析配置 (自定义API Host):")
        print(f"   API Host: {api_host.strip()}")
        print(f"   API Key: {api_key[:10]}... (已隐藏)")
        print(f"   Base URL: {base_url}")
    else:
        print(f"\n❌ 错误: API Host 格式不正确!")
        print(f"   当前格式: {api_config}")
        print(f"   正确格式: mh2k5ngr5k.re.qweatherapi.com,YOUR_API_KEY")
        exit(1)
else:
    # 使用免费开发版
    base_url = "https://devapi.qweather.com/v7"
    api_key = api_config.strip()
    print(f"\n2. 使用免费开发版 API:")
    print(f"   API Key: {api_key[:10]}... (已隐藏)")
    print(f"   Base URL: {base_url}")

print(f"\n3. 测试城市搜索 (查询 'Beijing'):")
print("-" * 60)

# 测试城市搜索
url = f"{base_url}/city/lookup"
params = {
    "location": "Beijing",
    "key": api_key,
    "lang": "zh"
}

try:
    response = requests.get(url, params=params, timeout=10)
    print(f"   请求URL: {url}")
    print(f"   请求参数: {params}")
    print(f"   响应状态: HTTP {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   响应数据: {data}")
        
        if data.get("code") == "200":
            locations = data.get("location", [])
            if locations:
                city = locations[0]
                location_id = city.get("id")
                print(f"\n✅ 城市搜索成功!")
                print(f"   城市名称: {city.get('name')}")
                print(f"   国家: {city.get('country')}")
                print(f"   Location ID: {location_id}")
                
                # 测试天气查询
                print(f"\n4. 测试天气查询 (LocationID: {location_id}):")
                print("-" * 60)
                
                weather_url = f"{base_url}/weather/now"
                weather_params = {
                    "location": location_id,
                    "key": api_key,
                    "lang": "zh"
                }
                
                weather_response = requests.get(weather_url, params=weather_params, timeout=10)
                print(f"   请求URL: {weather_url}")
                print(f"   请求参数: {weather_params}")
                print(f"   响应状态: HTTP {weather_response.status_code}")
                
                if weather_response.status_code == 200:
                    weather_data = weather_response.json()
                    print(f"   响应数据: {weather_data}")
                    
                    if weather_data.get("code") == "200":
                        now = weather_data.get("now", {})
                        print(f"\n✅ 天气查询成功!")
                        print(f"   温度: {now.get('temp')}°C")
                        print(f"   体感温度: {now.get('feelsLike')}°C")
                        print(f"   天气: {now.get('text')}")
                        print(f"   湿度: {now.get('humidity')}%")
                        print(f"   风向: {now.get('windDir')}")
                        print(f"   风力等级: {now.get('windScale')}")
                        
                        print("\n" + "=" * 60)
                        print("🎉 API 配置完全正确！可以正常使用天气功能了！")
                        print("=" * 60)
                    else:
                        print(f"\n❌ 天气查询失败!")
                        print(f"   错误代码: {weather_data.get('code')}")
                        print(f"   请检查 API Key 权限和余额")
                else:
                    print(f"\n❌ 天气查询 HTTP 错误: {weather_response.status_code}")
            else:
                print(f"\n❌ 未找到城市信息")
        else:
            print(f"\n❌ 城市搜索失败!")
            print(f"   错误代码: {data.get('code')}")
            error_codes = {
                "400": "请求错误，请检查参数",
                "401": "认证失败，API key无效",
                "402": "超过访问次数或余额不足",
                "403": "无访问权限",
                "404": "查询的数据不存在",
                "429": "超过限定的访问次数",
                "500": "服务器错误"
            }
            error_msg = error_codes.get(data.get("code"), "未知错误")
            print(f"   错误信息: {error_msg}")
    else:
        print(f"\n❌ HTTP 请求失败: {response.status_code}")
        print(f"   响应内容: {response.text}")

except requests.exceptions.Timeout:
    print(f"\n❌ 请求超时")
except Exception as e:
    print(f"\n❌ 发生错误: {str(e)}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)


