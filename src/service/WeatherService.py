import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class WeatherService:
    # 常用城市 Location ID 映射表（避免调用 city/lookup API）
    CITY_IDS = {
        # 中国主要城市
        "北京": "101010100", "beijing": "101010100",
        "上海": "101020100", "shanghai": "101020100",
        "广州": "101280101", "guangzhou": "101280101",
        "深圳": "101280601", "shenzhen": "101280601",
        "成都": "101270101", "chengdu": "101270101",
        "杭州": "101210101", "hangzhou": "101210101",
        "武汉": "101200101", "wuhan": "101200101",
        "西安": "101110101", "xian": "101110101", "xi'an": "101110101",
        "南京": "101190101", "nanjing": "101190101",
        "天津": "101030100", "tianjin": "101030100",
        "重庆": "101040100", "chongqing": "101040100",
        "苏州": "101190401", "suzhou": "101190401",
        "大连": "101070201", "dalian": "101070201",
        "青岛": "101120201", "qingdao": "101120201",
        "厦门": "101230201", "xiamen": "101230201",
        "郑州": "101180101", "zhengzhou": "101180101",
        "长沙": "101250101", "changsha": "101250101",
        "沈阳": "101070101", "shenyang": "101070101",
        "哈尔滨": "101050101", "harbin": "101050101",
        "昆明": "101290101", "kunming": "101290101",
        "南宁": "101300101", "nanning": "101300101",
        "济南": "101120101", "jinan": "101120101",
        "合肥": "101220101", "hefei": "101220101",
        "太原": "101100101", "taiyuan": "101100101",
        "石家庄": "101090101", "shijiazhuang": "101090101",
        
        # 港澳台
        "香港": "101320101", "hong kong": "101320101", "hongkong": "101320101",
        "澳门": "101330101", "macau": "101330101", "macao": "101330101",
        "台北": "101340101", "taipei": "101340101",
        
        # 国际主要城市
        "纽约": "newyork", "new york": "newyork",
        "伦敦": "london", "london": "london",
        "东京": "tokyo", "tokyo": "tokyo",
        "巴黎": "paris", "paris": "paris",
        "悉尼": "sydney", "sydney": "sydney",
        "新加坡": "singapore", "singapore": "singapore",
        "首尔": "seoul", "seoul": "seoul",
        "曼谷": "bangkok", "bangkok": "bangkok",
        "莫斯科": "moscow", "moscow": "moscow",
        "柏林": "berlin", "berlin": "berlin",
        "罗马": "rome", "rome": "rome",
        "马德里": "madrid", "madrid": "madrid",
        "多伦多": "toronto", "toronto": "toronto",
        "洛杉矶": "losangeles", "los angeles": "losangeles", "losangeles": "losangeles", "la": "losangeles",
        "旧金山": "sanfrancisco", "san francisco": "sanfrancisco", "sanfrancisco": "sanfrancisco",
        "芝加哥": "chicago", "chicago": "chicago",
        "华盛顿": "washington", "washington": "washington", "washington dc": "washington",
    }
    
    def __init__(self):
        # 和风天气认证配置
        # API_KEY 支持三种格式：
        # 1. API Host格式: mh2k5ngr5k.re.qweatherapi.com,YOUR_API_KEY
        # 2. 只有API Key: YOUR_API_KEY (自动使用免费开发版API)
        # 3. 只有API Host: mh2k5ngr5k.re.qweatherapi.com (不推荐)
        
        api_config = os.getenv("WEATHER_API_KEY", "")
        
        if not api_config:
            print("⚠️  WEATHER_API_KEY not configured in .env file")
            self.base_url = "https://devapi.qweather.com/v7"
            self.api_key = None
            return
        
        if "qweatherapi.com" in api_config:
            # 包含自定义 API Host
            if "," in api_config:
                # 格式: API_HOST,API_KEY
                api_host, api_key = api_config.split(",", 1)
                self.base_url = f"https://{api_host.strip()}/v7"
                self.api_key = api_key.strip()
                print(f"✅ Using custom API Host: {api_host.strip()}")
            else:
                # 只提供了 API Host，没有提供 API Key
                print(f"⚠️  Warning: API Host provided but no API Key found.")
                print(f"    Correct format: WEATHER_API_KEY=your_host,your_api_key")
                print(f"    Or just use: WEATHER_API_KEY=your_api_key (for free API)")
                self.base_url = f"https://{api_config.strip()}/v7"
                self.api_key = None
        else:
            # 只提供了 API Key，使用免费开发版 API
            self.base_url = "https://devapi.qweather.com/v7"
            self.api_key = api_config.strip()
            print(f"✅ Using standard free API with provided API Key")
    
    def get_weather(self, location, date=None):
        """
        获取指定地点的天气信息
        使用和风天气API
        """
        try:
            # 第一步：先搜索城市，获取 LocationID
            location_id = self._search_city(location)
            if not location_id:
                return f"找不到城市: {location}，请检查城市名称是否正确"
            
            print(f"Found location ID for {location}: {location_id}")
            
            # 第二步：使用 LocationID 查询天气
            if date is None:
                # 获取实时天气
                url = f"{self.base_url}/weather/now"
                params = {
                    "location": location_id,
                    "lang": "zh"  # 中文
                }
            else:
                # 获取3天天气预报
                url = f"{self.base_url}/weather/3d"
                params = {
                    "location": location_id,
                    "lang": "zh"
                }
            
            # 使用请求头传递 API Key（官方文档标准方式）
            headers = {
                "X-QW-Api-Key": self.api_key
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查API响应状态码
                if data.get("code") == "200":
                    return self._format_weather_data(data, date, location)
                else:
                    error_msg = self._get_error_message(data.get("code"))
                    print(f"API Error: {data}")  # 调试信息
                    return f"获取{location}天气失败: {error_msg}"
            else:
                return f"无法获取{location}的天气信息 (HTTP {response.status_code})"
                
        except requests.exceptions.Timeout:
            return f"获取{location}天气超时，请稍后重试"
        except Exception as e:
            print(f"Exception details: {str(e)}")  # 调试信息
            return f"获取{location}天气出错: {str(e)}"
    
    def _search_city(self, city_name):
        """
        搜索城市，获取 LocationID
        优先使用本地映射表，避免调用可能不可用的 city/lookup API
        """
        # 标准化城市名称（转小写）
        city_key = city_name.lower().strip()
        
        # 1. 先从本地映射表查找
        if city_key in self.CITY_IDS:
            location_id = self.CITY_IDS[city_key]
            print(f"✅ Found city in local map: {city_name} -> {location_id}")
            return location_id
        
        # 2. 如果本地没有，尝试API搜索（可能会失败）
        print(f"⚠️  City '{city_name}' not in local map, trying API lookup...")
        
        # 尝试使用自定义 API Host（如果配置了）
        if "qweatherapi.com" in self.base_url and "devapi" not in self.base_url:
            result = self._try_search_city(city_name, self.base_url)
            if result:
                return result
            
            print(f"⚠️  API lookup not available. Please use supported city names.")
        
        return None
    
    def _try_search_city(self, city_name, base_url):
        """
        尝试搜索城市（内部方法）
        """
        try:
            url = f"{base_url}/city/lookup"
            params = {
                "location": city_name,
                "lang": "zh"
            }
            
            # 使用请求头传递 API Key（官方文档标准方式）
            headers = {
                "X-QW-Api-Key": self.api_key
            }
            
            print(f"Trying URL: {url}")
            print(f"With params: {params}")
            print(f"With header: X-QW-Api-Key: {self.api_key[:10]}...")
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"City search response: {data}")  # 调试信息
                
                if data.get("code") == "200":
                    locations = data.get("location", [])
                    if locations:
                        # 返回第一个匹配的城市的 LocationID
                        city_info = locations[0]
                        print(f"✅ Found city: {city_info.get('name')} ({city_info.get('country')})")
                        return city_info.get("id")
                else:
                    error_msg = self._get_error_message(data.get("code"))
                    print(f"❌ City search API error: {error_msg} (code: {data.get('code')})")
            else:
                print(f"❌ City search HTTP error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
            
            return None
            
        except Exception as e:
            print(f"❌ City search exception: {str(e)}")
            return None
    
    def _format_weather_data(self, data, target_date=None, city_name=""):
        """
        格式化和风天气API返回的数据
        """
        if target_date is None:
            # 实时天气格式化
            now = data.get("now", {})
            
            temp = now.get("temp", "N/A")
            feels_like = now.get("feelsLike", "N/A")
            text = now.get("text", "N/A")  # 天气状况文字
            humidity = now.get("humidity", "N/A")
            wind_dir = now.get("windDir", "N/A")
            wind_scale = now.get("windScale", "N/A")
            pressure = now.get("pressure", "N/A")
            
            update_time = data.get("updateTime", "")
            
            weather_info = f"""
Current Weather in {city_name}

Temperature: {temp}°C (feels like {feels_like}°C)
Condition: {text}
Humidity: {humidity}%
Wind: {wind_dir} Level {wind_scale}
Pressure: {pressure} hPa

Last Update: {update_time}
"""
            return weather_info.strip()
        else:
            # 天气预报格式化
            daily = data.get("daily", [])
            if not daily:
                return "No forecast data available"
            
            weather_info = f"\nWeather Forecast for {city_name} (Next 3 Days)\n\n"
            
            for day in daily:
                date = day.get("fxDate", "N/A")
                temp_max = day.get("tempMax", "N/A")
                temp_min = day.get("tempMin", "N/A")
                text_day = day.get("textDay", "N/A")
                text_night = day.get("textNight", "N/A")
                humidity = day.get("humidity", "N/A")
                
                weather_info += f"""
Date: {date}
Temperature: {temp_min}°C ~ {temp_max}°C
Day: {text_day} | Night: {text_night}
Humidity: {humidity}%
---
"""
            
            return weather_info.strip()
    
    def _get_error_message(self, code):
        """
        根据和风天气API错误码返回错误信息
        """
        error_codes = {
            "400": "请求错误，请检查参数",
            "401": "认证失败，API key无效",
            "402": "超过访问次数或余额不足",
            "403": "无访问权限",
            "404": "查询的数据不存在",
            "429": "超过限定的访问次数",
            "500": "服务器错误"
        }
        return error_codes.get(code, f"未知错误 (code: {code})")