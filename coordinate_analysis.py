#!/usr/bin/env python3
"""
氣象站坐標分析程式
分析氣象站API (O-A0003-001)中的兩種坐標系統
"""

import os
import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import folium
from geopy.distance import geodesic
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class CoordinateAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('CWA_API_KEY')
        self.base_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
        self.dataset_id = "O-A0003-001"
        
    def fetch_weather_data(self):
        """獲取氣象站資料"""
        url = f"{self.base_url}/{self.dataset_id}"
        params = {
            'Authorization': self.api_key,
            'format': 'JSON'
        }
        
        try:
            response = requests.get(url, params=params, verify=False)  # 暫時跳過SSL驗證
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 請求失敗: {e}")
            return None
    
    def parse_dual_coordinates(self, data):
        """解析雙坐標系統資料"""
        if not data or 'records' not in data:
            return None
        
        stations = []
        records = data['records']['Station']
        
        for record in records:
            try:
                station_data = {
                    'station_id': record['StationId'],
                    'station_name': record['StationName'],
                    'location': record['GeoInfo']['CountyName'] + record['GeoInfo']['TownName'],
                    'observation_time': record['ObsTime']['DateTime'],
                    'temperature': float(record['WeatherElement']['AirTemperature']) if record['WeatherElement']['AirTemperature'] else None,
                    'humidity': float(record['WeatherElement']['RelativeHumidity']) if record['WeatherElement']['RelativeHumidity'] else None
                }
                
                # 解析兩種坐標系統
                coordinates = record['GeoInfo']['Coordinates']
                
                if len(coordinates) >= 2:
                    # 第一個坐標系統
                    coord1 = coordinates[0]
                    station_data.update({
                        'coord1_system': coord1.get('CoordinateSystem', 'Unknown'),
                        'coord1_lat': float(coord1['StationLatitude']),
                        'coord1_lon': float(coord1['StationLongitude'])
                    })
                    
                    # 第二個坐標系統
                    coord2 = coordinates[1]
                    station_data.update({
                        'coord2_system': coord2.get('CoordinateSystem', 'Unknown'),
                        'coord2_lat': float(coord2['StationLatitude']),
                        'coord2_lon': float(coord2['StationLongitude'])
                    })
                    
                    # 計算兩種坐標之間的距離（假設都是WGS84）
                    coord1_point = (station_data['coord1_lat'], station_data['coord1_lon'])
                    coord2_point = (station_data['coord2_lat'], station_data['coord2_lon'])
                    distance = geodesic(coord1_point, coord2_point).meters
                    
                    station_data['coordinate_distance_m'] = distance
                    
                elif len(coordinates) == 1:
                    # 只有一個坐標系統的情況
                    coord = coordinates[0]
                    station_data.update({
                        'coord1_system': coord.get('CoordinateSystem', 'Unknown'),
                        'coord1_lat': float(coord['StationLatitude']),
                        'coord1_lon': float(coord['StationLongitude']),
                        'coord2_system': coord.get('CoordinateSystem', 'Unknown'),
                        'coord2_lat': float(coord['StationLatitude']),
                        'coord2_lon': float(coord['StationLongitude']),
                        'coordinate_distance_m': 0.0
                    })
                
                stations.append(station_data)
                
            except (KeyError, ValueError, TypeError, IndexError) as e:
                print(f"解析站點資料時發生錯誤 {record.get('StationId', 'Unknown')}: {e}")
                continue
        
        return stations
    
    def analyze_coordinate_differences(self, stations_data):
        """分析坐標差異"""
        if not stations_data:
            return None
        
        # 計算統計資料
        distances = [s['coordinate_distance_m'] for s in stations_data if s['coordinate_distance_m'] > 0]
        
        if not distances:
            print("沒有找到坐標差異的測站")
            return None
        
        stats = {
            'total_stations': len(stations_data),
            'stations_with_diff_coords': len(distances),
            'mean_distance': np.mean(distances),
            'median_distance': np.median(distances),
            'std_distance': np.std(distances),
            'min_distance': np.min(distances),
            'max_distance': np.max(distances),
            'percentile_95': np.percentile(distances, 95),
            'percentile_99': np.percentile(distances, 99)
        }
        
        return stats, distances
    
    def create_dual_coordinate_map(self, stations_data):
        """建立雙坐標地圖"""
        if not stations_data:
            return None
        
        # 計算地圖中心
        all_lats = [s['coord1_lat'] for s in stations_data] + [s['coord2_lat'] for s in stations_data]
        all_lons = [s['coord1_lon'] for s in stations_data] + [s['coord2_lon'] for s in stations_data]
        
        center_lat = np.mean(all_lats)
        center_lon = np.mean(all_lons)
        
        # 建立地圖
        m = folium.Map(location=[center_lat, center_lon], zoom_start=8)
        
        # 添加兩種坐標的測站
        for station in stations_data:
            # 第一個坐標系統 - 藍色標記
            folium.CircleMarker(
                location=[station['coord1_lat'], station['coord1_lon']],
                radius=6,
                popup=f"{station['station_name']}<br>坐標系統1: {station['coord1_system']}<br>"
                      f"緯度: {station['coord1_lat']:.6f}<br>經度: {station['coord1_lon']:.6f}<br>"
                      f"溫度: {station['temperature']}°C",
                color='blue',
                fill=True,
                fillColor='blue',
                fillOpacity=0.7
            ).add_to(m)
            
            # 第二個坐標系統 - 紅色標記
            folium.CircleMarker(
                location=[station['coord2_lat'], station['coord2_lon']],
                radius=6,
                popup=f"{station['station_name']}<br>坐標系統2: {station['coord2_system']}<br>"
                      f"緯度: {station['coord2_lat']:.6f}<br>經度: {station['coord2_lon']:.6f}<br>"
                      f"距離差異: {station['coordinate_distance_m']:.2f}m",
                color='red',
                fill=True,
                fillColor='red',
                fillOpacity=0.7
            ).add_to(m)
            
            # 如果距離差異很大，畫連線
            if station['coordinate_distance_m'] > 10:  # 距離差異超過10公尺
                folium.PolyLine(
                    locations=[
                        [station['coord1_lat'], station['coord1_lon']],
                        [station['coord2_lat'], station['coord2_lon']]
                    ],
                    color='green',
                    weight=2,
                    opacity=0.5,
                    popup=f"距離差異: {station['coordinate_distance_m']:.2f}m"
                ).add_to(m)
        
        # 添加圖例
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>坐標系統圖例</h4>
        <p><i class="fa fa-circle" style="color:blue"></i> 坐標系統1</p>
        <p><i class="fa fa-circle" style="color:red"></i> 坐標系統2</p>
        <p><i class="fa fa-minus" style="color:green"></i> 坐標差異連線</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def create_distance_analysis_plot(self, distances, stats):
        """建立距離分析圖表"""
        plt.figure(figsize=(15, 10))
        
        # 1. 距離分佈直方圖
        plt.subplot(2, 2, 1)
        plt.hist(distances, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(stats['mean_distance'], color='red', linestyle='--', label=f'平均: {stats["mean_distance"]:.2f}m')
        plt.axvline(stats['median_distance'], color='green', linestyle='--', label=f'中位數: {stats["median_distance"]:.2f}m')
        plt.xlabel('坐標距離差異 (公尺)')
        plt.ylabel('測站數量')
        plt.title('氣象站坐標距離差異分佈')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 2. 累積分佈函數
        plt.subplot(2, 2, 2)
        sorted_distances = np.sort(distances)
        cumulative = np.arange(1, len(sorted_distances) + 1) / len(sorted_distances)
        plt.plot(sorted_distances, cumulative, linewidth=2, color='darkblue')
        plt.xlabel('坐標距離差異 (公尺)')
        plt.ylabel('累積概率')
        plt.title('坐標距離差異累積分佈')
        plt.grid(True, alpha=0.3)
        
        # 添加重要百分位數標記
        for percentile in [50, 75, 90, 95, 99]:
            value = np.percentile(distances, percentile)
            plt.axvline(value, color='red', linestyle=':', alpha=0.7)
            plt.text(value, 0.5, f'{percentile}%: {value:.1f}m', rotation=90, 
                    verticalalignment='center', fontsize=8)
        
        # 3. 統計摘要表格
        plt.subplot(2, 2, 3)
        plt.axis('off')
        stats_text = f"""
        統計摘要
        ================================
        總測站數: {stats['total_stations']}
        有坐標差異的測站: {stats['stations_with_diff_coords']}
        
        距離統計 (公尺):
        平均值: {stats['mean_distance']:.2f}
        中位數: {stats['median_distance']:.2f}
        標準差: {stats['std_distance']:.2f}
        最小值: {stats['min_distance']:.2f}
        最大值: {stats['max_distance']:.2f}
        
        百分位數:
        95%: {stats['percentile_95']:.2f}m
        99%: {stats['percentile_99']:.2f}m
        """
        plt.text(0.1, 0.9, stats_text, transform=plt.gca().transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace')
        
        # 4. 距離分類圓餅圖
        plt.subplot(2, 2, 4)
        distance_categories = {
            '0-10m': len([d for d in distances if d <= 10]),
            '10-50m': len([d for d in distances if 10 < d <= 50]),
            '50-100m': len([d for d in distances if 50 < d <= 100]),
            '100-500m': len([d for d in distances if 100 < d <= 500]),
            '>500m': len([d for d in distances if d > 500])
        }
        
        # 過濾掉數量為0的類別
        distance_categories = {k: v for k, v in distance_categories.items() if v > 0}
        
        if distance_categories:
            colors = ['lightgreen', 'yellow', 'orange', 'lightcoral', 'red']
            plt.pie(distance_categories.values(), labels=distance_categories.keys(), 
                   autopct='%1.1f%%', colors=colors[:len(distance_categories)])
            plt.title('坐標距離差異分類')
        
        plt.tight_layout()
        return plt
    
    def save_results(self, stations_data, stats, distances):
        """儲存分析結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 儲存CSV資料
        df = pd.DataFrame(stations_data)
        csv_file = f"outputs/coordinate_analysis_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"資料已儲存至: {csv_file}")
        
        # 儲存統計結果
        stats_file = f"outputs/coordinate_stats_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"統計結果已儲存至: {stats_file}")
        
        return csv_file, stats_file

def main():
    """主程式"""
    print("開始分析氣象站坐標系統...")
    
    try:
        # 初始化分析器
        analyzer = CoordinateAnalyzer()
        
        # 獲取資料
        print("正在從 CWA API 獲取資料...")
        raw_data = analyzer.fetch_weather_data()
        
        if raw_data:
            print("成功獲取資料，正在解析...")
            
            # 解析雙坐標資料
            stations_data = analyzer.parse_dual_coordinates(raw_data)
            
            if stations_data:
                print(f"成功解析 {len(stations_data)} 個測站資料")
                
                # 分析坐標差異
                result = analyzer.analyze_coordinate_differences(stations_data)
                
                if result:
                    stats, distances = result
                    
                    print("\n=== 坐標差異分析結果 ===")
                    print(f"總測站數: {stats['total_stations']}")
                    print(f"有坐標差異的測站: {stats['stations_with_diff_coords']}")
                    print(f"平均距離差異: {stats['mean_distance']:.2f} 公尺")
                    print(f"中位數距離差異: {stats['median_distance']:.2f} 公尺")
                    print(f"最大距離差異: {stats['max_distance']:.2f} 公尺")
                    print(f"95%的測站差異小於: {stats['percentile_95']:.2f} 公尺")
                    
                    # 建立地圖視覺化
                    print("\n正在建立地圖...")
                    map_viz = analyzer.create_dual_coordinate_map(stations_data)
                    if map_viz:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        map_file = f"outputs/coordinate_comparison_map_{timestamp}.html"
                        map_viz.save(map_file)
                        print(f"地圖已儲存至: {map_file}")
                    
                    # 建立統計圖表
                    print("正在建立統計圖表...")
                    plt = analyzer.create_distance_analysis_plot(distances, stats)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    plot_file = f"outputs/coordinate_analysis_plot_{timestamp}.png"
                    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
                    plt.close()
                    print(f"統計圖表已儲存至: {plot_file}")
                    
                    # 儲存結果
                    analyzer.save_results(stations_data, stats, distances)
                    
                    # 顯示距離差異最大的前10個測站
                    print("\n=== 距離差異最大的前10個測站 ===")
                    stations_with_diff = [s for s in stations_data if s['coordinate_distance_m'] > 0]
                    stations_with_diff.sort(key=lambda x: x['coordinate_distance_m'], reverse=True)
                    
                    for i, station in enumerate(stations_with_diff[:10]):
                        print(f"{i+1}. {station['station_name']}")
                        print(f"   距離差異: {station['coordinate_distance_m']:.2f} 公尺")
                        print(f"   坐標1: {station['coord1_system']} ({station['coord1_lat']:.6f}, {station['coord1_lon']:.6f})")
                        print(f"   坐標2: {station['coord2_system']} ({station['coord2_lat']:.6f}, {station['coord2_lon']:.6f})")
                        print()
                    
                else:
                    print("坐標差異分析失敗")
            else:
                print("解析資料失敗")
        else:
            print("獲取資料失敗")
            
    except Exception as e:
        print(f"程式執行發生錯誤: {e}")

if __name__ == "__main__":
    main()
