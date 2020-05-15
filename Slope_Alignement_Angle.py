#Slope Alignment Angle represents the trail's alignment to the slope of the surrounding hill. 
    #a lot of information gets created here, so it needs to be deleted
    #the output should only be a new column in the trail files



def SAA(ply, dem):
#Empty fields are created as intermediate place holders that will be deleted later on.
    arcpy.AddField_management(ply, "trlOr", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.AddField_management(ply, "trlDir", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.AddField_management(ply, "LocID", "SHORT", "", "", "", "", "NULLABLE", "REQUIRED")
    #The line segments need to each have a unique id for geoprocessing of their individual directions.
    exp="autoIncrement(!LocID!)"
    cb = """def autoIncrement(var):
        global rec 
        pStart = 1  
        pInterval = 1 
        if (rec == 0):  
            rec = pStart  
        else:  
            rec += pInterval  
        return rec """
    arcpy.CalculateField_management(ply, "LocID", exp, "PYTHON3", cb)
    
    #Find the averaged direction the trail is pinting in
    arcpy.DirectionalMean_stats(ply, "trail_dir.shp", "DIRECTION", "LocID")
    
    arcpy.JoinField_management(ply, "LocID", "trail_dir.shp", "LocID")
    arcpy.CalculateField_management(ply, "trlDir", '!CompassA!', "PYTHON3")
    arcpy.Delete_management("trail_dir.shp")
    
    #the average direction the trail's slope points in can be used to compare to the trails direction.
    outasp=arcpy.sa.Aspect(dem)
    outasp.save("aspec.tif")
    
    #Average all aspect values of the cells which intersect with the line segments. 
    arcpy.AddSurfaceInformation_3d(ply, "aspec.tif", "Z_MEAN", "LINEAR")
    arcpy.AddField_management(ply, "aspect", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.CalculateField_management(ply, "aspect", '!Z_MEAN!', "PYTHON3")
    arcpy.Delete_management("aspec.tif")

    #Simply finding the difference betwween the two orientations can generate orientation of the trail to the slope.
    arcpy.CalculateField_management(ply, "trlOr", '!trlDir! - !aspect!', "PYTHON3")
    arcpy.AddField_management(ply, "trl_ang", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
   
   #for simplicities sake, the orientation was converted to a 0-90 degree scale.
   expression = "direction(!trlOr!)"
    codeblock = """def direction(var):
        if var >= 0 and var < 90:
            return var
        elif var >= 90 and var < 180:
            return ((var-180)*-1)
        elif var >= 180 and var < 270:
            return (var-180)
        elif var >= 270 and var < 360:
            return ((var-360)*-1)
        elif var < 0 and var >= -90:
            return (var * -1)
        elif var < -90 and var >= -180:
            return (var+180)
        elif var <-180 and var >= -270:
            return ((var+180)*-1)
        elif var <-270 and var >= -360:
            return (var+360)
        elif var < -360:
            return -99999 """


    arcpy.CalculateField_management(ply, "trl_ang", expression, "PYTHON3", codeblock)
    
    #Delete all the superfluous data created to preserve memory
    arcpy.DeleteField_management(ply, ["trlOr","LocID_1", "trlDir", 
                                              "aspect", "id_1", 
                                              "CompassA", "DirMean", "CirVar", 
                                              "AveX", "AveY", "Z_Mean", "AveLen", 
                                              "Teststat", "RefValue", "PValue",
                                              "UnifTest", "Id"])
    print("trailangle finished")
