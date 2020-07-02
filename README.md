# Description

I want to have a wordcount program that I ran to split a big file into piece to number of jobs thru k8s and then return the final count.

Below is the rough idea:

1. Ask for an input file and ask number of threads. If the file is small than 10K rows, just use one pod by default
2. Send a file to a pod that would just split it into piece, those pieces would be send back to the host like _0,_1,....  
3. The python will collect those pieces and issues number of pod along with those files to ask them to calculate the
 wordcount. Finally, those pod would return the summary of the wordcount
4. The python script would collect the result in piece and put it all into one file. Send the file into a pod and have 
 the pod to do sort of uniq and then sum. Return the final result to python again 
5. Display the result 

Trying to use k8s to do calculation as much as possible. 
