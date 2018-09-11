import glob
import os
import math
from functools import reduce
import struct
import sys

#import plotly.offline as po
#import plotly.graph_objs as go

def getFileSize(fname):
	return os.path.getsize(fname)

def gcd_list(numbers):
    return reduce(math.gcd, numbers)

def convert_to_csv(fname,startsize,loopsize):
	outFileName = fname+".csv"
	if(os.path.exists(outFileName)):
		return
	readFile = open(fname,"rb")
	wFile = open(outFileName,"w")

	readFile.seek(startsize)
	try:
		while True:
			for i in range(0,int(loopsize/4)):
				value = struct.unpack_from("f",readFile.read(4))[0]
				wFile.write(str(value))
				wFile.write(",")
			wFile.write("\n")
	except Exception:
		readFile.close()
		wFile.close()

def convert_mem_to_csv(fname,data,cherryPick):
	outFileName = fname+".csv"
	#if(os.path.exists(outFileName)):
	#	return
	wFile = open(outFileName,"w")
	wFile.write("index,max,min,Tag,\n")
	index = 0
	for dataline in data:
		if( (dataline["max"] != dataline["min"]) or not cherryPick ):
			wFile.write(str(index)+",")
			wFile.write(str(dataline["max"])+",")
			wFile.write(str(dataline["min"])+",")
			if(str(index) in profiles.keys()):
				wFile.write(profiles[str(index)][0] + ",")
			else:
				wFile.write(" ,")
			for v in dataline["datas"]:
				wFile.write(str(v)+",")
			wFile.write("\n")
		index = index + 1

def readRPL(fname,startsize,loopsize):
	readFile = open(fname,"rb")
	ret = []

	readFile.seek(startsize)
	try:
		while True:
			for i in range(0,int(loopsize/4)):
				value = struct.unpack_from("f",readFile.read(4))[0]
				if len(ret) <= i:
					ret.append({"max":value, "min":value,"datas":[] })
				ret[i]["datas"].append(value)
				ret[i]["max"] = max(ret[i]["max"],value)
				ret[i]["min"] = min(ret[i]["min"],value)
	except Exception:
		readFile.close()
	return ret

#def makeGrafHtml(fname,datas):
#    grafFname = fname + "_glaf.html"
#    trace = []
#    index = 0
#    times = []
#    for i in range(len(datas[0]["datas"])):
#        times.append(i)
#    for dataline in datas:
#        profilename = ""
#        if(str(index) in profiles.keys()):
#            profilename = profiles[str(index)][IDProfileSlot]
#        trace.append(go.Scatter(
#            x = times,
#            y = dataline["datas"],
#            name = str(index)+"_"+profilename ))
#        index = index + 1
#    # layoutを作成
#    layout = go.Layout(
#        # デフォルトでは描画領域が狭いのでmarginを0に
#        margin=dict(
#            l=0,
#            r=0,
#            b=0,
#            t=0
#        )
#    )
#    # traceとlayoutからfigureを作成
#    fig = go.Figure(data= trace, layout=layout)
#    # プロット
#    po.plot(fig, filename=grafFname,auto_open=False)

def getConvertedValue(profileIndex,value):
	if(str(profileIndex) in profiles.keys()):
		return "{0:.3f}".format(value * profiles[str(profileIndex)][multpleProfileSlot] + profiles[str(profileIndex)][diffProfileSlot])
	else:
		return "{0:.3f}".format(value )

def makeMotion3Json(fname,datas):
	motionFileName = fname + ".motion3.json"
	FPS = 10.0
	Duration = datas[921]["datas"][-1]
	wFile = open(motionFileName,"w")
	wFile.write("{\n")
	wFile.write("	\"Version\": 3,\n")
	wFile.write("	\"Meta\": {\n")
	wFile.write("		\"Duration\": "+ getConvertedValue(921,Duration) +",\n")
	wFile.write("		\"Fps\": " + str(FPS) + ",\n")
	wFile.write("		\"FadeInTime\": 1.0,\n")
	wFile.write("		\"FadeOutTime\": 1.0,\n")
	wFile.write("		\"Loop\": true,\n")
	wFile.write("		\"AreBeziersRestricted\": true,\n")

	#種類数計算
	Curves = len(profiles) - 1
	wFile.write("		\"CurveCount\": " + str(Curves) + ",\n")
	#総セグメント数（セグメントはライン数　１ラインのポイント数　－　1　*　カーブ数
	Segments = ( len(datas[971]["datas"]) * 2 ) * Curves
	wFile.write("		\"TotalSegmentCount\": " + str(Segments) + ",\n")
	#総ポイント数 
	Points = ( len(datas[971]["datas"]) * 3 - 1 ) * Curves
	wFile.write("		\"TotalPointCount\": " + str(Points) + ",\n")

	wFile.write("		\"UserDataCount\": 0,\n")
	wFile.write("		\"TotalUserDataSize\": 0\n")
	wFile.write("	},\n")
	wFile.write("	\"Curves\": [\n")
	index = 0
	for line in datas:
		if( (str(index) in profiles.keys()) and (index != 921) ):
			wFile.write("		{\n")
			wFile.write("			\"Target\": \"Parameter\",\n")
			wFile.write("			\"Id\": \"" + profiles[str(index)][IDProfileSlot] + "\",\n")
			wFile.write("			\"Segments\": [\n")
			wFile.write("				0,\n")
			wFile.write("				" + getConvertedValue(index,line["datas"][0]) + ",\n")
			for i in range( 1,len(line["datas"])-1):
				wFile.write("				0,\n")
				wFile.write("				" + getConvertedValue(921,datas[921]["datas"][i]) + ",\n")
				wFile.write("				" + getConvertedValue(index,line["datas"][i]) + ",\n")
			wFile.write("			]\n")
			wFile.write("		},\n")
		index = index + 1
	
	wFile.write("	]\n")
	wFile.write("}")
	wFile.close()
	
def getCalcedValue(line,datas,index):
	ret = 0.0
	for ele in line["Element"]:
		eleValue = datas[ele[0]]["datas"][index] * ele[1] + ele[2]
		ret = ret + eleValue
	return "{0:.3f}".format(ret )

def makeMotion3Json2(fname,datas,selectIdType,outMultiParams):
	motionFileName = fname + selectIdType + ".motion3.json"
	FPS = 10.0
	Duration = datas[921]["datas"][-1]
	wFile = open(motionFileName,"w")
	wFile.write("{\n")
	wFile.write("	\"Version\": 3,\n")
	wFile.write("	\"Meta\": {\n")
	wFile.write("		\"Duration\": "+ getConvertedValue(921,Duration) +",\n")
	wFile.write("		\"Fps\": " + str(FPS) + ",\n")
	wFile.write("		\"FadeInTime\": 1.0,\n")
	wFile.write("		\"FadeOutTime\": 1.0,\n")
	wFile.write("		\"Loop\": true,\n")
	wFile.write("		\"AreBeziersRestricted\": true,\n")

	#種類数計算
	Curves = len(profiles) - 1
	wFile.write("		\"CurveCount\": " + str(Curves) + ",\n")
	#総セグメント数（セグメントはライン数　１ラインのポイント数　－　1　*　カーブ数
	Segments = ( len(datas[971]["datas"]) * 2 ) * Curves
	wFile.write("		\"TotalSegmentCount\": " + str(Segments) + ",\n")
	#総ポイント数 
	Points = ( len(datas[971]["datas"]) * 3 - 1 ) * Curves
	wFile.write("		\"TotalPointCount\": " + str(Points) + ",\n")

	wFile.write("		\"UserDataCount\": 0,\n")
	wFile.write("		\"TotalUserDataSize\": 0\n")
	wFile.write("	},\n")
	wFile.write("	\"Curves\": [\n")
	for line in outMultiParams:
		wFile.write("		{\n")
		wFile.write("			\"Target\": \"Parameter\",\n")
		wFile.write("			\"Id\": \"" + line[selectIdType] + "\",\n")
		wFile.write("			\"Segments\": [\n")
		wFile.write("				0,\n")
		wFile.write("				" + getCalcedValue(line,datas,0) + ",\n")		
		for i in range( 1,len(datas[921]["datas"])-1):
			wFile.write("				0,\n")
			wFile.write("				" + getConvertedValue(921,datas[921]["datas"][i]) + ",\n")
			wFile.write("				" + getCalcedValue(line,datas,i) + ",\n")
		wFile.write("			]\n")
		wFile.write("		},\n")

	#index = 0
	#for line in datas:
	#	if( (str(index) in profiles.keys()) and (index != 921) ):
	#		wFile.write("		{\n")
	#		wFile.write("			\"Target\": \"Parameter\",\n")
	#		wFile.write("			\"Id\": \"" + profiles[str(index)][IDProfileSlot] + "\",\n")
	#		wFile.write("			\"Segments\": [\n")
	#		wFile.write("				0,\n")
	#		wFile.write("				" + getConvertedValue(index,line["datas"][0]) + ",\n")
	#		for i in range( 1,len(line["datas"])-1):
	#			wFile.write("				0,\n")
	#			wFile.write("				" + getConvertedValue(921,datas[921]["datas"][i]) + ",\n")
	#			wFile.write("				" + getConvertedValue(index,line["datas"][i]) + ",\n")
	#		wFile.write("			]\n")
	#		wFile.write("		},\n")
	#	index = index + 1
	
	wFile.write("	]\n")
	wFile.write("}")
	wFile.close()

def simpleLineOver(targetFname,OverIndex,datas,startSize,LoopSize):
	baseFile = open(targetFname,"rb")
	wFileName =targetFname + "_" + str(OverIndex) + "nk.rpl"
	wFile = open(wFileName,"wb")
	for i in range(int(startSize / 4)):
		wFile.write(baseFile.read(4))
	try:
		loops = 0
		while True:
			for i in range(int(LoopSize / 4)):
				if(i == OverIndex):
					value = baseFile.read(4)
					struct.unpack_from("f",value)[0]
					overdata = (loops / 20)% 2.0 - 1.0
					wFile.write(struct.pack("f",overdata))
				else:					
					value = baseFile.read(4)
					struct.unpack_from("f",value)[0]
					wFile.write(value)
			loops = loops + 1
	except Exception:
		baseFile.close()
		wFile.close()

multpleProfileSlot = 2
diffProfileSlot = 3
IDProfileSlot = 1
profiles = {"921":["Time","Time",1,0]}
#profiles["115"] =["ParamBodyAngleX","PARAM_BODY_ANGLE_X",(10/45),0]#?
#profiles["5"] =["ParamBodyAngleZ","PARAM_BODY_ANGLE_Z",-20,10]
##profiles["28"] = ["ParamEyeLOpen","PARAM_EYE_L_OPEN",-1,1]
#profiles["29"] = ["ParamEyeROpen","PARAM_EYE_R_OPEN",-1,1]
#profiles["1"] = ["ParamAngleX","PARAM_ANGLE_X",-60,30]
##profiles["0"] = ["ParamAngleY","PARAM_ANGLE_Y",-60,30]
#profiles["2"] = ["ParamAngleZ","PARAM_ANGLE_Z",-60,30]
#profiles["13"] = ["ParamMouthOpenY","PARAM_MOUTH_OPEN_Y",1,0]
#profiles["8"] = ["ParamMouthForm","PARAM_MOUTH_FORM",2,-1]
#profiles["36"] = ["ParamEyeBallX","PARAM_EYE_BALL_X",-2,1]
#profiles["37"] = ["ParamEyeBallY","PARAM_EYE_BALL_Y",-2,1]
#profiles["66"] = ["ParamArmL","PARAM_ARM_L",1,0]
#profiles["55"] = ["ParamArmR","PARAM_ARM_R",1,0]
#profiles["68"] = ["ParamHandL","PARAM_HAND_L",20,-10]
#profiles["53"] = ["ParamHandR","PARAM_HAND_R",20,-10]
#profiles["48"] = ["ParamCheek","PARAM_CHEEK",1,0]
#profiles["49"] = ["ParamTear","PARAM_TEAR",1,0]
#profiles["50"] = ["ParamRage","PARAM_RAGE",1,0]
#profiles["51"] = ["ParamHairFluffy","PARAM_HAIR_FLUFFY",1,0]
#profiles[""] = ["","PARAM_EYE_FORM",1,0]
#profiles[""] = ["","PARAM_BROW_L_Y",1,0]
#profiles[""] = ["","PARAM_BROW_R_Y",1,0]
#profiles[""] = ["","PARAM_BROW_L_X",1,0]
#profiles[""] = ["","PARAM_BROW_R_X",1,0]
#profiles[""] = ["","PARAM_BROW_L_ANGLE",1,0]
#profiles[""] = ["","PARAM_BROW_R_ANGLE",1,0]
#profiles[""] = ["","PARAM_BROW_L_FORM",1,0]
#profiles[""] = ["","PARAM_BROW_R_FORM",1,0]

outMultiParams = []
outMultiParams.append({"ID2":"PARAM_BODY_ANGLE_X","ID3":"ParamBodyAngleX","Element":[[115,(10/45),0]]})
outMultiParams.append({"ID2":"PARAM_BODY_ANGLE_Z","ID3":"ParamBodyAngleZ","Element":[[5,-20,10]]})
outMultiParams.append({"ID2":"PARAM_EYE_L_OPEN","ID3":"ParamEyeLOpen","Element":[[ 28,-1,1 ]]})
outMultiParams.append({"ID2":"PARAM_EYE_R_OPEN","ID3":"ParamEyeROpen","Element":[[ 29,-1,1 ]]})
outMultiParams.append({"ID2":"PARAM_ANGLE_X","ID3":"ParamAngleX","Element":[[ 1,-60,30 ]]})
outMultiParams.append({"ID2":"PARAM_ANGLE_Y","ID3":"ParamAngleY","Element":[[ 0,-60,30 ]]})
outMultiParams.append({"ID2":"PARAM_ANGLE_Z","ID3":"ParamAngleZ","Element":[[ 2,-60,30 ]]})
outMultiParams.append({"ID2":"PARAM_MOUTH_OPEN_Y","ID3":"ParamMouthOpenY","Element":[[ 13,1,0 ]]})
outMultiParams.append({"ID2":"PARAM_MOUTH_FORM","ID3":"ParamMouthForm","Element":[[ 8,-2,1 ]]})
outMultiParams.append({"ID2":"PARAM_EYE_BALL_X","ID3":"ParamEyeBallX","Element":[[ 36,-2,1 ]]})
outMultiParams.append({"ID2":"PARAM_EYE_BALL_Y","ID3":"ParamEyeBallY","Element":[[ 37,-2,1 ]]})
outMultiParams.append({"ID2":"PARAM_ARM_L","ID3":"ParamArmL","Element":[[ 66,1,0 ]]})
outMultiParams.append({"ID2":"PARAM_ARM_R","ID3":"ParamArmR","Element":[[ 55,1,0 ]]})
outMultiParams.append({"ID2":"PARAM_HAND_L","ID3":"ParamHandL","Element":[[ 68,20,-10 ]]})
outMultiParams.append({"ID2":"PARAM_HAND_R","ID3":"ParamHandR","Element":[[ 53,20,-10 ]]})
outMultiParams.append({"ID2":"PARAM_CHEEK","ID3":"ParamCheek","Element":[[ 48,1,0 ]]})
outMultiParams.append({"ID2":"PARAM_TEAR","ID3":"ParamTear","Element":[[ 49,1,0 ]]})
outMultiParams.append({"ID2":"PARAM_RAGE","ID3":"ParamRage","Element":[[ 50,1,0 ]]})
outMultiParams.append({"ID2":"PARAM_HAIR_FLUFFY","ID3":"ParamHairFluffy","Element":[[ 51,1,0 ]]})

outMultiParams.append({"ID2":"PARAM_EYE_FORM","ID3":"ParamEyeForm","Element":[[ 20,-0.5,0 ], [ 20,-0.5,0 ], [ 22,+0.5,0 ], [ 23,+0.5,0 ]]})
outMultiParams.append({"ID2":"PARAM_BROW_L_Y","ID3":"ParamBrowLY","Element":[[ 20,-0.5,0 ], [ 24,-0.5,0 ], [ 22,+0.5,0 ], [ 26,+0.5,0 ]]})
outMultiParams.append({"ID2":"PARAM_BROW_R_Y","ID3":"ParamBrowRY","Element":[[ 21,-0.5,0 ], [ 25,-0.5,0 ], [ 23,+0.5,0 ], [ 27,+0.5,0 ]]})
outMultiParams.append({"ID2":"PARAM_BROW_L_ANGLE","ID3":"ParamBrowLAngle","Element":[[ 20,-0.5,0 ], [ 22,+0.5,0 ]]})
outMultiParams.append({"ID2":"PARAM_BROW_R_ANGLE","ID3":"ParamBrowRAngle","Element":[[ 21,-0.5,0 ], [ 23,+0.5,0 ]]})
outMultiParams.append({"ID2":"PARAM_BROW_L_FORM","ID3":"ParamBrowLForm","Element":[[ 20,-0.5,0 ], [ 24,-0.5,0 ], [ 22,+0.5,0 ], [ 26,+0.5,0 ]]})
outMultiParams.append({"ID2":"PARAM_BROW_R_FORM","ID3":"ParamBrowRForm","Element":[[ 21,-0.5,0 ], [ 25,-0.5,0 ], [ 23,+0.5,0 ], [ 27,+0.5,0 ]]})

folderPath = "Set Your rpl files folder path."

fileList = glob.glob(folderPath+"\\*.rpl")

fileSizes = []
for f in fileList:
	fileSizes.append(getFileSize(f))
	print(f+":"+ str(fileSizes[len(fileSizes)-1]))

fileSizes.sort()

print(fileSizes)
fileDiffSizes = []

for i in range(1,len(fileSizes)):
	fileDiffSizes.append(fileSizes[i] - fileSizes[0])

diffSize = gcd_list(fileDiffSizes)
print(diffSize)

sSize = 0
for i in range(0,len(fileSizes)):
	sSize = fileSizes[i] % diffSize
	print(fileSizes[i] % diffSize)

for f in fileList:
	print(f)
	#convert_to_csv(f,sSize,diffSize)
	datas = readRPL(f,sSize,diffSize)
	convert_mem_to_csv(f,datas,True)
	#makeGrafHtml(f,datas)
	makeMotion3Json2(f,datas,"ID2",outMultiParams)
	makeMotion3Json2(f,datas,"ID3",outMultiParams)

#f = fileList[-1]
#datas = readRPL(f,sSize,diffSize)
#print(len(datas))
#for i in range(len(datas)):
#	print(i)
#	if(datas[i]["min"] != datas[i]["max"]):
#		simpleLineOver(fileList[-1],i,datas,sSize,diffSize)

print("end")