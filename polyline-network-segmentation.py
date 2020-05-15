#the trail lines are too long to make any reasonable analysis possble. Therefore
#the lines needed to be segmented into smaller sections. Per common 
#literature, 100ft segments seem resonable to make observations
#regarding trail quality. 
#there is no specific function in arcpy to cut all lines in a 
#shapefile by a defined interval. I needed to call a polyline
#method to return segments and write them to a new shapefile.
#a case field was used to later summarize and join the smaller lines 
#back to the original trail file. 

#sr is the spatial reference
#distance is the interval length you wish to cut by

def network_segment(infeat, outname, sr, id_field, distance):
    segments=arcpy.CreateFeatureclass_management(env.workspace, outname+"_seg.shp", "POLYLINE", "", "", "", sr)
    arcpy.AddField_management(segments, id_field, "TEXT", 100, "", "", "", "NULLABLE", "REQUIRED")
#The first cursor allows teh script to acces the attribute records of the existing polyline shapefile.
    cursor = arcpy.da.SearchCursor(infeat, ['SHAPE@', id_field])
    for row in cursor:
    #Establishing the start and finsih distance define the intervals of the segment.
    #distance is the length we want our segments to be. It defines the first endpoint and then
      #increases the start/finish points to capture the proceeding segments.
        x=distance
        start=0
        finish=distance
        length=row[0].length
        pnt_lst=[]
        while x<length:
            pos=row[0].positionAlongLine(x)
            pnt_lst.append(pos)
            x+=distance
        #the second cursor accesses the attribute table of the newly created shapefile.
        ins = arcpy.da.InsertCursor(splt_pts,['SHAPE@', id_field])
        Pid=row[1]
        for i in pnt_lst:
            ins.insertRow([i, Pid])
        del ins
        seg_lst=[]
        while finish < length:
            seg=row[0].segmentAlongLine(start, finish)
            seg_lst.append(seg)
            start+=distance
            finish+=distance
        ins2= arcpy.da.InsertCursor(segments,['SHAPE@', id_field])
        for y in seg_lst:
            ins2.insertRow([y, Pid])
        del ins2
    del cursor
    print("Trails have been segmented")
