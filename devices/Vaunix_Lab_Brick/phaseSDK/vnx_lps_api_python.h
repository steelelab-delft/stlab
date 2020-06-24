//	Include file for LabBrick digital phase shifter API
//
// (c) 2008 - 2013 by Vaunix Corporation, all rights reserved
//
// modified by Felix Schmidt, felix.e.schmidt@gmail.com 05/2019

void fnLPS_SetTestMode(bool testmode);
int fnLPS_GetNumDevices();
int fnLPS_GetDevInfo(unsigned int *ActiveDevices);
int fnLPS_GetModelNameA(unsigned int deviceID, char *ModelName);
int fnLMS_GetModelNameW(unsigned int deviceID, wchar_t *ModelName);
int fnLPS_InitDevice(unsigned int deviceID);
int fnLPS_CloseDevice(unsigned int deviceID);
int fnLPS_GetSerialNumber(unsigned int deviceID);
int fnLPS_GetDeviceStatus(unsigned int deviceID);
int fnLPS_GetDLLVersion();


int fnLPS_SetPhaseAngle(unsigned int deviceID, int phase);
int fnLPS_SetWorkingFrequency(unsigned int deviceID, int frequency);
int fnLPS_SetRampStart(unsigned int deviceID, int rampstart);
int fnLPS_SetRampEnd(unsigned int deviceID, int rampstop);
int fnLPS_SetPhaseAngleStep(unsigned int deviceID, int phasestep);
int fnLPS_SetPhaseAngleStepTwo(unsigned int deviceID, int phasestep2);
int fnLPS_SetDwellTime(unsigned int deviceID, int dwelltime);
int fnLPS_SetDwellTimeTwo(unsigned int deviceID, int dwelltime2);
int fnLPS_SetIdleTime(unsigned int deviceID, int idletime);
int fnLPS_SetHoldTime(unsigned int deviceID, int holdtime);

int fnLPS_SetProfileElement(unsigned int deviceID, int index, int phaseangle);
int fnLPS_SetProfileCount(unsigned int deviceID, int profilecount);
int fnLPS_SetProfileIdleTime(unsigned int deviceID, int idletime);
int fnLPS_SetProfileDwellTime(unsigned int deviceID, int dwelltime);
int fnLPS_StartProfile(unsigned int deviceID, int mode);

int fnLPS_SetRampDirection(unsigned int deviceID, bool up);
int fnLPS_SetRampMode(unsigned int deviceID, bool mode);
int fnLPS_SetRampBidirectional(unsigned int deviceID, bool bidir_enable);
int fnLPS_StartRamp(unsigned int deviceID, bool go);

int fnLPS_SaveSettings(unsigned int deviceID);

int fnLPS_GetPhaseAngle(unsigned int deviceID);
int fnLPS_GetWorkingFrequency(unsigned int deviceID);

int fnLPS_GetRampStart(unsigned int deviceID);
int fnLPS_GetRampEnd(unsigned int deviceID);
int fnLPS_GetDwellTime(unsigned int deviceID);
int fnLPS_GetDwellTimeTwo(unsigned int deviceID);
int fnLPS_GetIdleTime(unsigned int deviceID);
int fnLPS_GetHoldTime(unsigned int deviceID);
int fnLPS_GetPhaseAngleStep(unsigned int deviceID);
int fnLPS_GetPhaseAngleStepTwo(unsigned int deviceID);

int fnLPS_GetProfileElement(unsigned int deviceID, int index);
int fnLPS_GetProfileCount(unsigned int deviceID);
int fnLPS_GetProfileDwellTime(unsigned int deviceID);
int fnLPS_GetProfileIdleTime(unsigned int deviceID);
int fnLPS_GetProfileIndex(unsigned int deviceID);

int fnLPS_GetMaxPhaseShift(unsigned int deviceID);
int fnLPS_GetMinPhaseShift(unsigned int deviceID);
int fnLPS_GetMinPhaseStep(unsigned int deviceID);

int fnLPS_GetMaxWorkingFrequency(unsigned int deviceID);
int fnLPS_GetMinWorkingFrequency(unsigned int deviceID);