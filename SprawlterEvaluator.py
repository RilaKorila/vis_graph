from graph_info  import *
import glob
import math

# 定数
NN_ALPHA = 0.25
NE_ALPHA = 0.25
EE_ALPHA = 0.1

NN_RATIO = 1.0
NE_RATIO = 1.0
EE_RATIO = 1.0
EE_RATIO2 = 0.5
EE_RATIO3 = 0.0
	

maxne = 0.0
maxee = 0.0
# counter = 0



# グローバル変数
# retrieve file names
path =  "./sample_data2/*"
filenames = glob.glob(path)
# path = './graph_23'
# filenames = [path]

# pythonなら配列の長さ指定が不要かも
result = [0.0] * len(filenames)
result2 = [0.0] * len(filenames)
result3 = [0.0] * len(filenames)
sprawls = [0.0] * len(filenames)
nnpens = [0.0] * len(filenames)
nepens = [0.0] * len(filenames)
eepens = [0.0] * len(filenames)

# Calculate sprawl：空間の粗密度を計算
def calcSprawl(meta_node_info):
    sprawl = 0.0
    minx = 1.0e+30
    miny = 1.0e+30
    maxx = -1.0e+30
    maxy = -1.0e+30

    for i in meta_node_info.keys():
        # metaノードの情報を渡したい
        meta_node = meta_node_info[i]
        pos = meta_node["pos"]
        r =  float(meta_node["r"])
        x1 = pos[0] - r
        x2 = pos[0] + r
        y1 = pos[1] - r
        y2 = pos[1] + r

        minx = minx if minx < x1 else x1
        miny = miny if miny < y1 else y1
        maxx = maxx if maxx > x2 else x2
        maxy = maxy if maxy > y2 else y2
        # CHECK: グラフ全体の範囲を知りたいなら、maxx, maxyはx2, y2を使った方がイメージと近い
        # maxx = maxx if maxx > x2 else x2
        # maxy = maxy if maxy > y2 else y2

    # CHECK: sprawl = (maxx - minx) * (maxy - miny) / graph.nodes.size();の graph.nodes.size
    # metaノードの大きさ？
    sprawl = (maxx - minx) * (maxy - miny) / float(r*2)
    return sprawl

def calcNodeNodePenalty(phase, meta_node_info):
    penalty = 0.0
    p0 = 0.0
    maxnn = 0.0

    # for each vertex pair
    for i in meta_node_info.keys():
        meta_node1 = meta_node_info[i]
        pos1 = meta_node1["pos"]
        r1 =  float(meta_node1["r"])

        for j in range(i+1, len(meta_node_info.keys())):
            meta_node2 = meta_node_info[j]
            pos2 = meta_node2["pos"]
            r2 =  float(meta_node2["r"])

            # calculate distance between circles
            diffr = (r1 - r2) if r1 > r2 else r2 - r1
            # print('---------- i: ' +  str(i)  + '-- j: ' + str(j) + '------')
            # print(pos1)
            # print(pos2)
            
            # 二つのノードの中心間距離
            # dist = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
            dist = calc_distance(pos1, pos2)
            if (r1 + r2) < dist:
                continue

            # if a circle encloses another circle
            if dist < diffr:
                if r1 > r2:
                    p0 = math.sqrt(r2 * r2 * math.pi)
                    continue
                else:
                    p0 = math.sqrt(r1 * r1 * math.pi)
                    continue
            
            # if circles partially overlap
            else:
                # print('r1: ' + str(r1) +  '     r2: ' + str(r2) +  '   dist: ' + str(dist))
                cos1 = (dist * dist + r1 * r1 - r2 * r2) / (2 * dist * r1)
                cos2 = (dist * dist + r2 * r2 - r1 * r1) / (2 * dist * r2)
                p0 = r1 * r1 * math.acos(cos1) + r2 * r2 * math.acos(cos2) - 0.5 * math.sqrt(4 * dist * dist * r1 * r1 - (dist * dist + r1 * r1 - r2 * r2) * (dist * dist + r1 * r1 - r2 * r2))

            # Add the penalty
            if phase == 1:
                maxnn = maxnn if maxnn > p0 else p0
            else:
                p0 = (1 - NN_ALPHA) * math.pow((2.0 * p0), 0.7) + NN_ALPHA * math.pow(maxnn, 0.7)
            
            penalty += p0
        
    return penalty

# Calculate node-edge overlap penalty
def calcNodeEdgePenalty(object1, phase, meta_node_info):
    penalty = 0.0
    linelist = object1['ori']['linelist']
    nodelist = object1['ori']['nodelist']


    # for each edge
    # edge: edge両端のnode_id
    for edge in linelist:
        maxne = 0.0
        ex1 = nodelist[edge[0]][CX]
        ey1 = nodelist[edge[0]][CY]
        ex2 = nodelist[edge[1]][CX]
        ey2 = nodelist[edge[1]][CY]
        ea = ex2 - ex1
        eb = ey2 - ey1
        ec = -(ea * ex1 + eb * ey1)

        # for each vertex
        for i, node in enumerate(nodelist):
            meta_node = meta_node_info[nodelist[i][NODE_GROUP]]
            c = meta_node["pos"]
            r =  float(meta_node["r"])
            D = math.fabs(ea * c[0] + eb * c[1] + ec)
            eab = ea* ea + eb * eb
            det = eab * r * r - D * D

            if det <= 0.0:
                continue
            det = math.sqrt(det)
            cx1 = c[0] + (ea * D - eb * det) / eab
            cy1 = c[1] + (eb * D + ea * det) / eab
            cx2 = c[0] + (ea * D + eb * det) / eab
            cy2 = c[1] + (eb * D - ea * det) / eab
            if cx1 > ex1 and cx1 > ex2 and cx2 > ex1 and cx2 > ex2:
                continue
            if cx1 < ex1 and cx1 < ex2 and cx2 < ex1 and cx2 < ex2:
                continue
            len = calc_distance((cx1, cy1), (cx1, cy2))

            if(phase == 1):
                maxne = maxne if maxne > len else len
            else:
                len = 2.0 * (1.0 - NE_ALPHA) * len + NE_ALPHA * maxne
            penalty += len

    return penalty

# Calculate edge-edge overlap penalty
def calcEdgeEdgePenalty(object1):
    PENALTY_CONST = 1.0
    penalty = 0.0
    linelist = object1['ori']['linelist']
    nodelist = object1['ori']['nodelist']

    # for each edge pair
    for i, edge1 in enumerate(linelist):
        x11 = nodelist[edge1[0]][CX]
        y11 = nodelist[edge1[0]][CY]
        x12 = nodelist[edge1[1]][CX]
        y12 = nodelist[edge1[1]][CY]
        x1v = x12 - x11
        y1v = y12 - y11
        # edgeの長さを三平方で計算
        len1 = math.sqrt(x1v * x1v + y1v * y1v)

        for j in range(i+1, len(linelist)):
            edge2 = linelist[j]
            x21 = nodelist[edge2[0]][CX]
            y21 = nodelist[edge2[0]][CY]
            x22 = nodelist[edge2[1]][CX]
            y22 = nodelist[edge2[1]][CY]
            
            # check the intersection: 交差があるか検証
            s = (x11 - x12) * (y21 - y11) - (y11 - y12) * (x21 - x11)
            t = (x11 - x12) * (y22 - y11) - (y11 - y12) * (x22 - x11)
            if s * t > 0:
                continue
            s = (x21 - x22) * (y11 - y21) - (y21 - y22) * (x11 - x21)
            t = (x21 - x22) * (y12 - y21) - (y21 - y22) * (x12 - x21)
            if s * t > 0:
                continue
			
            # calculate the inner product as the penalty
            x2v = x22 - x21
            y2v = y22 - y21
            len2 = math.sqrt(x2v * x2v + y2v * y2v)
            inner = math.fabs(x1v * x2v + y1v * y2v) / (len1 * len2) + PENALTY_CONST
            penalty += inner
    
    return penalty

# Normalize penalty
def normalizePenalty():
    nnmin = 1.0e+30
    nnmax = -1.0e+30
    nemin = 1.0e+30
    nemax = -1.0e+30
    eemin = 1.0e+30
    eemax = -1.0e+30
    MIN = 1.0
    MAX = 10.0
    EPSILON = 0.001

    for i in range(len(result)):
        nnmin = nnmin if nnmin < nnpens[i] else nnpens[i]
        nemin = nemin if nemin < nepens[i] else nepens[i]
        eemin = eemin if eemin < eepens[i] else eepens[i]
        nnmax = nnmax if nnmax > nnpens[i] else nnpens[i]
        nemax = nemax if nemax > nepens[i] else nepens[i]
        eemax = eemax if eemax > eepens[i] else eepens[i]

    print(nnpens)
    print(eepens)
    print(nepens)

    #  for each graph
    for i in range(len(result)):
        vnn = (nnpens[i] - nnmin) / (nnmax - nnmin)
        vne = (nepens[i] - nemin) / (nemax - nemin)
        vee = (eepens[i] - eemin) / (eemax - eemin)
        vnn = vnn * (MAX - MIN) + MIN
        vne = vne * (MAX - MIN) + MIN
        vee = vee * (MAX - MIN) + MIN
        nnpens[i] = math.sqrt(sprawls[i] * vnn)
        nepens[i] = math.sqrt(sprawls[i] * vne)
        eepens[i] = math.sqrt(sprawls[i] * vee)
        result[i] = NN_RATIO * nnpens[i] + NE_RATIO * nepens[i] + EE_RATIO * eepens[i]
        result2[i] = NN_RATIO * nnpens[i] + NE_RATIO * nepens[i] + EE_RATIO2 * eepens[i]
        result3[i] = NN_RATIO * nnpens[i] + NE_RATIO * nepens[i] + EE_RATIO3 * eepens[i]
    
        # print(filenames[i] + "," + str(result[i]) + "," + str(result2[i]) + "," + str(result3[i]) + "," + str(nnpens[i]) + "," + str(nepens[i]) + "," + str(eepens[i]))
        return result2[i]


# Evaluate one graph
def calcPenaltyOneGraph(object1, phase, counter, meta_node_info):
    # print(object1["ori"]["nodelist"][0:4])
    sprawl = calcSprawl(meta_node_info)
    nnpen = calcNodeNodePenalty(phase, meta_node_info)
    nepen = calcNodeEdgePenalty(object1, phase, meta_node_info)
    eepen = calcEdgeEdgePenalty(object1)

    sprawls[counter] = sprawl
    nnpens[counter] = nnpen
    nepens[counter] = nepen
    eepens[counter] = eepen


def main(): 
    # calculate penalty (first)
    for counter, file in enumerate(filenames):
        object1 = get_object(file)
        meta_node_info = calc_meta_node(object1["ori"])
        # minr = 10000.0
        # for i in range(len(meta_node_info.keys())):
        #     print('----------  No. ' + str(i) + '  ---------------')
        #     # print(meta_node_info[i]["nodes"])
        #     # prCint(meta_node_info[i]["pos"])
        #     print(meta_node_info[i]["r"])
        #     minr = minr if (meta_node_info[i]["r"] > 0.1 and minr < meta_node_info[i]["r"]) else meta_node_info[i]["r"]
        # print("------- minr -----", minr)
        calcPenaltyOneGraph(object1, 1, counter, meta_node_info)
        
        if counter % 1000 == 0:
            print(" #caclPenaltyOneGraph (phase 1) " + str(counter) + "/" + str(len(filenames)))

    # calculate penalty (second phase)
    for counter, file in enumerate(filenames):
        object1 = get_object(file)
        meta_node_info = calc_meta_node(object1["ori"])
        calcPenaltyOneGraph(object1, 2, counter, meta_node_info)
        
        if counter % 1000 == 0:
            print(" #caclPenaltyOneGraph (phase 2) " + str(counter) + "/" + str(len(filenames)))


    # normalize penalty
    res = normalizePenalty()
    return res

# main()