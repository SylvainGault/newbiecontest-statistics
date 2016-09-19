MKDIR=mkdir -p
RM=rm -f
RMDIR=rmdir
GNUPLOT=gnuplot
#DOWNLOAD=curl --silence "$(1)" --output "$(2)"
DOWNLOAD=wget --quiet --show-progress --progress=dot:binary "$(1)" --output-document="$(2)"

FIGDIR=fig
SCRIPTDIR=scripts
GNUPLOTDIR=gnuplot
GNUPLOTDATADIR=$(GNUPLOTDIR)/data
GNUPLOTINC=$(GNUPLOTDIR)/common.plt

PLOTS=validation_alltime_histo_yearly\
      validation_alltime_histo_monthly\
      validation_alltime_smooth\
      validation_year_avg_histo_monthy\
      validation_year_avg_smooth\
      validation_week_avg_histo_daily\
      validation_week_avg_smooth\
      validation_day_avg_histo_hourly\
      validation_day_avg_smooth\
      registration_alltime_histo_yearly\
      registration_alltime_smooth\
      registration_year_avg_histo_monthy\
      registration_year_avg_smooth\
      registration_week_avg_histo_daily\
      registration_week_avg_smooth\
      registration_day_avg_histo_hourly\
      registration_day_avg_smooth

GNUPLOTDATA=$(patsubst %,$(GNUPLOTDATADIR)/%.data,$(PLOTS))
GNUPLOTPLTS=$(patsubst %,$(GNUPLOTDIR)/%.plt,$(PLOTS))
GNUPLOTFIGS=$(patsubst %,$(FIGDIR)/%.png,$(PLOTS))

MINIDUMPURL=https://www.newbiecontest.org/minidump.php
MINIDUMP=minidump.xml.bz2

POINTSTABLEURL=https://www.newbiecontest.org/index.php?page=calculpoints
POINTSTABLE=pointstable.html

SQLITEDB=minidump.db
XMLBZ2_DB=$(SCRIPTDIR)/xmlbz2_db.py




.PHONY: all
all: $(GNUPLOTFIGS)


$(MINIDUMP):
	$(call DOWNLOAD,$(MINIDUMPURL),$@)


$(POINTSTABLE):
	$(call DOWNLOAD,$(POINTSTABLEURL),$@)


$(SQLITEDB): $(XMLBZ2_DB) $(MINIDUMP) $(POINTSTABLE)
	$< $@ $(MINIDUMP) $(POINTSTABLE)


$(GNUPLOTDATADIR) $(FIGDIR):
	$(MKDIR) $@


.SECONDARY: $(GNUPLOTDATA)
$(GNUPLOTDATADIR)/%.data: $(SCRIPTDIR)/%.py $(SQLITEDB) | $(GNUPLOTDATADIR)
	$^ $@


$(FIGDIR)/%.png: $(GNUPLOTDIR)/%.plt $(GNUPLOTDATADIR)/%.data $(GNUPLOTINC) | $(FIGDIR)
	$(GNUPLOT) -d -e 'load "$(GNUPLOTINC)"'\
		-e 'set output "$@"'\
		-e 'filename = "$(GNUPLOTDATADIR)/$*.data"'\
		$<



.PHONY: clean
clean:
	$(RM) $(GNUPLOTFIGS)
	$(RMDIR) $(FIGDIR) 2>/dev/null || true
	$(RM) $(GNUPLOTDATA)
	$(RMDIR) $(GNUPLOTDATADIR) 2>/dev/null || true
	$(RM) $(SQLITEDB)

.PHONY: mrproper
mrproper: clean
	$(RM) $(MINIDUMP) $(POINTSTABLE)
