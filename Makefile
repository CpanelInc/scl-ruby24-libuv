OBS_PROJECT := EA4
OBS_PACKAGE := scl-ruby24-libuv
DISABLE_BUILD := arch=i586 repository=CentOS_8 repository=CentOS_6.5_standard
include $(EATOOLS_BUILD_DIR)obs.mk
