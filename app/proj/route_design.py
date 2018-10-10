# -*- coding:utf-8 -*-
"""
Created on Mon Jul 30 18:12:08 2018

@origin_author: Han DONG
@flask_version: Haozhou WANG
"""

import math
import pandas as pd

def route_design(locations, H=30.0, long_fov=61.9, short_fov=46.4, side_overlap=80.0, head_overlap=85.0, time=2.0):
    """
    
    parameters
    -------
    locations: list of 4 end points
        e.g. [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    H: height of flight (unit: meter)
    long_fov: long field of view 
        [unit]: degree
    short_fov: short field of view 
        [unit]: degree
    side_overlap: side overlap rate (旁向重叠率) 
        [unit]: percent
    head_overlap: heading overlap rate(航向重叠率)
        [unit]: percent
    time: picture taking interval time 
        [unit]: second
    """
    # to be continued
    lon_A = XA = locations[0][0]
    lat_A = YA = locations[0][1]
    lon_B = XB = locations[1][0]
    lat_B = YB = locations[1][1]
    lon_C = XC = locations[2][0]
    lat_C = YC = locations[2][1]
    lon_D = XD = locations[3][0]
    lat_D = YD = locations[3][1]
    
    d1 = calc_distance(lat_A,lon_A, lat_B, lon_B)
    d2 = calc_distance(lat_A,lon_A, lat_C, lon_C)
    
    # ==========================================
    # 在指定飞行高度条件下获取的照片所具有的长度
    # ==========================================
    
    # 长方形照片中长边所包含的长度范围
    l1 = round(2*H*(math.tan((long_fov/2)*math.pi/180))) 
    # 长方形照片中短边所包含的长度范围
    l2 = round(2*H*(math.tan((short_fov/2)*math.pi/180))) 
    # 指定旁向重叠率所照片剩余的长度
    W1 = round(l1*(1-(side_overlap/100))) 
    # 指定航向重叠率所照片剩余的长度
    W2 = round(l2*(1-(head_overlap/100))) 
    
    v = W2 / time  # 飞行速度计算

    d3 = d1 + W1
    d4 = d2 + W1

    D = d1 + 2*W1

    m = math.ceil(D/W1) # 飞行路线中飞行节点个数
    
    # ==================
    # 飞行区域的边界扩充
    # ==================

    XA1 = (d3*XA - W1*XB)/d1
    YA1 = (d3*YA - W1*YB)/d1
    XB1 = XA+(d3*(XB-XA)/d1)
    YB1 = YA+(d3*(YB-YA)/d1)
    XC1 = (d3*XC - W1*XD)/d1
    YC1 = (d3*YC - W1*YD)/d1
    XD1 = XC+(d3*(XD-XC)/d1)
    YD1 = YC+(d3*(YD-YC)/d1)

    XA2 = (d4*XA1-W1*XC1)/d2
    YA2 = (d4*YA1-W1*YC1)/d2
    XB2 = (d4*XB1-W1*XD1)/d2
    YB2 = (d4*YB1-W1*YD1)/d2
    XC2 = XA1+(d4*(XC1-XA1)/d2)
    YC2 = YA1+(d4*(YC1-YA1)/d2)
    XD2 = XB1+(d4*(XD1-XB1)/d2)
    YD2 = YB1+(d4*(YD1-YB1)/d2)
    
    # 飞机航向角计算，机头与正北方向的夹角
    heading = round(90-math.atan((YC2-YA2)/(XC2-XA2))*180/math.pi)
    
    df_litchi = pd.DataFrame(columns=["latitude","longitude","altitude(m)","heading(deg)","curvesize(m)",
                                      "rotationdir","gimbalmode","gimbalpitchangle"] + 
                                      [j for i in range(1,16) for j in ['actiontype'+str(i), "actionparam"+str(i)]] +
                                      ["altitudemode","speed(m/s)","poi_latitude","poi_longitude",
                                      "poi_altitude(m)", "poi_altitudemode"])
    litchi_constant_values = ["NaN"] + [0]*3 + [-1,0]*15 + [0,v] + [0]*4 
    
    for i in range(0,m+1):
        XAi = XA2 + ((XB2-XA2)/D)*W1*i
        YAi = YA2 + ((YB2-YA2)/D)*W1*i
        XCi = XC2 + ((XD2-XC2)/D)*W1*i
        YCi = YC2 + ((YD2-YC2)/D)*W1*i
        
        a_side_points = [YAi,XAi,H,heading] + litchi_constant_values
        c_side_points = [YCi,XCi,H,heading] + litchi_constant_values
        
        if (i-1)%2 == 1:
            df_litchi.loc[len(df_litchi)] = a_side_points
            df_litchi.loc[len(df_litchi)] = c_side_points
        else:             
            df_litchi.loc[len(df_litchi)] = c_side_points
            df_litchi.loc[len(df_litchi)] = a_side_points
    
    return df_litchi
    
    
def calc_distance(Lat_A,Lng_A,Lat_B,Lng_B):
    
    ra = 6378140.0
    rb = 6356755.0
    
    flatten = (ra - rb) / ra
    
    rad_lat_A = math.radians(Lat_A)
    rad_lng_A = math.radians(Lng_A)
    
    rad_lat_B = math.radians(Lat_B)
    rad_lng_B = math.radians(Lng_B)
    
    pA = math.atan(rb / ra * math.tan(rad_lat_A))
    pB = math.atan(rb / ra * math.tan(rad_lat_B))
    
    xx = math.acos(math.sin(pA)*math.sin(pB)+math.cos(pA)*math.cos(pB)*math.cos(rad_lng_A - rad_lng_B))
    
    c1 = (math.sin(xx) - xx) * (math.sin(pA) + math.sin(pB)) ** 2 / math.cos(xx / 2) ** 2
    c2 = (math.sin(xx) - xx) * (math.sin(pA) - math.sin(pB)) ** 2 / math.sin(xx / 2) ** 2
    
    dr = flatten / 8 * (c1 - c2)
    
    distance = ra * (xx + dr)
    
    return distance
    
if __name__ == "__main__":
    litchi = route_design([[115.9599905, 42.96231622],
                           [115.9613017, 42.9620202],
                           [115.9603925, 42.96327818],
                           [115.961703,  42.9629824]])
    litchi.to_csv('litchi.csv', index=False)