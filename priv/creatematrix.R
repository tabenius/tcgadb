user="www"
pass="mahametta"
setwd(Sys.getenv('TCGAticketdir'))
cancertype=as.integer(Sys.getenv('TCGAcancer'))
mrnaplatform = as.integer(Sys.getenv('TCGAmrna'))
cnaplatform = as.integer(Sys.getenv('TCGAcna'))

require(RMySQL)
t0All <- Sys.time()
dbcon <- dbConnect(MySQL(max.con=1), user=user, password=pass, dbname="TCGA", host="localhost")

#sql <- paste("select id from cancer where name='",dbEscapeStrings(dbcon,cancer),"' limit 1",sep='')
#cancertype <- dbGetQuery(dbcon, sql)
#if (length(cancertype) != 1) 
#  stop(paste("Cancer",cancer,"not found"))
#cancertype=cancertype$id
cat("cancerid:",cancertype,"\n")

t0 <- Sys.time()
sql <- paste("select distinct patid from aliquot where cancid=",cancertype," and platfid=",cnaplatform," and samplid=2")
pat.cna <- dbGetQuery(dbcon, sql)
cat("n1:",length(pat.cna$patid),"\n")
sql <- paste("select distinct patid from aliquot where cancid=",cancertype," and platfid=",mrnaplatform," and samplid=2")
pat.mrna <- dbGetQuery(dbcon, sql)
cat("n2:",length(pat.mrna$patid),"\n")
Tpat <- Sys.time() - t0
patients <- unique(pat.mrna$patid)
patients2 <- unique(pat.cna$patid)
pats <- sort(intersect(patients,patients2))
N <- length(pats)

t0 <- Sys.time()
sql <- paste("select distinct gene from aliquot,cna where cna.aliqid=aliquot.id and cancid=",cancertype," and platfid=",cnaplatform," and samplid=2")
print(sql,stderr())
gen.cna <- dbGetQuery(dbcon, sql)
print(gen.cna)
#Tcnagen <- Sys.time() - t0
#t0 <- Sys.time()
sql <- paste("select distinct gene from aliquot,mRNA where mRNA.aliqid=aliquot.id and cancid=",cancertype," and platfid=",mrnaplatform," and samplid=2")
print(sql,stderr())
gen.mrna <- dbGetQuery(dbcon, sql)
print(gen.mrna)
Tgen <- Sys.time() - t0
gens <- sort(intersect(unique(gen.mrna$gene), unique(gen.cna$gene)))
p <- length(gens)
cat("p:",p,"\n")

#select distinct gene from (select gene from aliquot,cna where cna.aliqid=aliquot.id and cancid=18 and platfid=14 and samplid=2
#union select gene from aliquot,mRNA where mRNA.aliqid=aliquot.id and cancid=18 and platfid=17 and samplid=2) as foo;


# below was slower locally, perhaps it is faster with less bw sending small queries over net
#
#t0 <- Sys.time(); 
#res <- dbGetQuery(dbcon,'drop temporary table if exists gtmp');
#res <- dbGetQuery(dbcon,'create temporary table gtmp (gene int) storage memory');
#sql <- paste('insert into gtmp values (',paste(gens,collapse='),('), ')',sep='')
#res <- dbGetQuery(dbcon, sql)

#for(i in 1:200) {
#lab <- dbGetQuery(dbcon, paste("select name from gene,gtmp where id=gtmp.gene order by id")); 
#}
#Tlabgen <- Sys.time() - t0

#t0 <- Sys.time(); 
#for (i in 1:200) {
sql <- paste("select name from gene where id in (",paste(gens, collapse=","),") order by id")
print(sql,stderr())
lab <- dbGetQuery(dbcon, sql); 
#}
#Tlabgen <- Sys.time() - t0

Y <- array(-99, dim=c(N,p))
U <- array(-99, dim=c(N,p))
i <- 1
skipped <- NULL
for (pat in 1:N) {
  cat(paste(pat,"/",N,"\n"))
  # barcode of vial and portion of sample if divided into 100-120mg sample portions, just get first
  barcode <- dbGetQuery(dbcon,paste("select barcode from aliquot where cancid=",cancertype," and platfid=",cnaplatform," and samplid=2 and patid =",pats[pat]," order by substring(barcode,16,4) limit 1"))
  sql.cna <- paste("SELECT gene, value FROM cna, aliquot WHERE ",
		   "aliquot.id=cna.aliqid and cancid=",cancertype,
		   " and platfid=",cnaplatform,
		   " and samplid=2 and patid=",pats[pat],
		   " and gene in (",paste(gens,collapse=","),")",
		   " and barcode='",barcode,"' ORDER BY gene",sep='')
  pat1u <- dbGetQuery(dbcon, sql.cna)

  barcode <- dbGetQuery(dbcon,paste("select barcode from aliquot where cancid=",cancertype," and platfid=",mrnaplatform," and samplid=2 and patid =",pats[pat],"order by substring(barcode,16,4) limit 1"))
  sql.mrna <- paste("SELECT gene, value FROM mRNA, aliquot WHERE ",
		    "aliquot.id=mRNA.aliqid AND cancid=",cancertype,
		    " AND platfid=",mrnaplatform,
		    " AND samplid=2",
		    " AND patid=",pats[pat],
		    " AND gene in (",paste(gens,collapse=","),")",
		    " AND barcode='",barcode,"' ORDER BY gene",sep='')
  pat1y <- dbGetQuery(dbcon, sql.mrna)
  if (dim(pat1u)[1] != p | dim(pat1u)[1] != p) {
    skipped <- c(skipped, pat)
  } else {
    U[pat,] <- pat1u$value
    Y[pat,] <- pat1y$value
  }
}
tcancer <- Sys.time() - t0All
print(tcancer)
cat("Saving R data file...")
save(list=c("Y","U","lab"),file=paste('cancer.Rdata',sep=''))
cat("OK\n")
res <- list(Y=Y,U=U,lab=lab)
require(R.matlab)
cat("Saving matlab data file...")
writeMat('cancer.mat',y=res$Y,u=res$U,lab=res$lab)
cat("OK\n")
dbDisconnect(dbcon)

