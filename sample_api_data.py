#!/usr/bin/env python3
"""
獲取氣象站API樣本資料以分析坐標結構
"""

import requests
import json
from datetime import datetime

def get_sample_data():
    """獲取樣本API資料"""
    # 使用公開的API端點進行測試
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
    params = {
        'Authorization': 'CWA-Your-API-Key',  # 這會失敗，但我們可以看到錯誤訊息
        'format': 'JSON'
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # 儲存樣本資料
            with open('outputs/sample_api_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("樣本資料已儲存")
            return data
        else:
            print(f"API請求失敗: {response.text}")
            return None
            
    except Exception as e:
        print(f"錯誤: {e}")
        return None

def analyze_coordinate_structure():
    """分析坐標結構"""
    print("分析氣象站API坐標結構...")
    
    # 嘗試獲取樣本資料
    sample_data = get_sample_data()
    
    if sample_data and 'records' in sample_data and 'Station' in sample_data['records']:
        stations = sample_data['records']['Station']
        
        if len(stations) > 0:
            first_station = stations[0]
            
            print("\n=== 測站坐標結構分析 ===")
            print(f"測站ID: {first_station.get('StationId', 'N/A')}")
            print(f"測站名稱: {first_station.get('StationName', 'N/A')}")
            
            # 檢查GeoInfo結構
            if 'GeoInfo' in first_station:
                geo_info = first_station['GeoInfo']
                print(f"\nGeoInfo 鍵值: {list(geo_info.keys())}")
                
                # 檢查Coordinates結構
                if 'Coordinates' in geo_info:
                    coordinates = geo_info['Coordinates']
                    print(f"Coordinates 型態: {type(coordinates)}")
                    
                    if isinstance(coordinates, list):
                        print(f"坐標數量: {len(coordinates)}")
                        for i, coord in enumerate(coordinates):
                            print(f"\n坐標 {i+1}:")
                            print(f"  坐標系統: {coord.get('CoordinateSystem', 'N/A')}")
                            print(f"  緯度: {coord.get('StationLatitude', 'N/A')}")
                            print(f"  經度: {coord.get('StationLongitude', 'N/A')}")
                    else:
                        print(f"坐標內容: {coordinates}")
            
            # 顯示完整結構
            print(f"\n=== 完整測站結構 ===")
            print(json.dumps(first_station, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    analyze_coordinate_structure()
