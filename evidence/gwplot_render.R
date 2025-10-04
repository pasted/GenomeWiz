#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(optparse)
  # Install from GitHub in your R env: remotes::install_github("kcleal/gwplot"); remotes::install_github("kcleal/gw")
  library(gwplot)  # your plotting helpers
  library(gw)      # data helpers / loaders
  library(ggplot2)
})

option_list <- list(
  optparse::make_option("--sv_id", type="character"),
  optparse::make_option("--chrom", type="character"),
  optparse::make_option("--pos1", type="integer"),
  optparse::make_option("--pos2", type="character", default=""),
  optparse::make_option("--sample_id", type="character"),
  optparse::make_option("--out_png", type="character"),
  optparse::make_option("--out_svg", type="character")
)
opt <- optparse::parse_args(optparse::OptionParser(option_list=option_list))

# ---- TODO: Replace the following with real GWPlot/GW utilities ----
# Example: df <- gw::fetch_region(sample_id=opt$sample_id, chrom=opt$chrom, start=opt$pos1-2000, end=as.integer(opt$pos2 %||% opt$pos1+2000))
# p <- gwplot::sv_panel(df, sv_id=opt$sv_id, chrom=opt$chrom, pos1=opt$pos1, pos2=ifelse(opt$pos2=="", NA, as.integer(opt$pos2)))

p <- ggplot() + 
  ggplot2::annotate("text", x=0, y=0, label=paste0("SV: ", opt$sv_id,"  ", opt$chrom, ":", opt$pos1, ifelse(nchar(opt$pos2)>0, paste0("-", opt$pos2), ""))) +
  ggplot2::theme_minimal(base_size = 14)

ggsave(filename=opt$out_png, plot=p, width=8, height=4, dpi=150)
ggsave(filename=opt$out_svg, plot=p, width=8, height=4, dpi=150)
cat("Rendered:", opt$out_png, "and", opt$out_svg, "\n")
