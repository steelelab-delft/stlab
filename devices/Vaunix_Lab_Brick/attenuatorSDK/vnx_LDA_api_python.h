// Include file for 64 Bit Vaunix Lab Brick LDA Synthesizer DLL
//
// 10/2013	RD	64 Bit DLL version.
//
// modified by Felix Schmidt, felix.e.schmidt@gmail.com 05/2019


void fnLDA_SetTraceLevel(int tracelevel, int IOtracelevel, bool verbose);

void fnLDA_SetTestMode(bool testmode);
int fnLDA_GetNumDevices();
int fnLDA_GetDevInfo(unsigned int *ActiveDevices);
int fnLDA_GetModelNameA(unsigned int deviceID, char *ModelName);
int fnLDA_GetModelNameW(unsigned int deviceID, wchar_t *ModelName);
int fnLDA_InitDevice(unsigned int deviceID);
int fnLDA_CloseDevice(unsigned int deviceID);
int fnLDA_GetSerialNumber(unsigned int deviceID);
int fnLDA_GetDLLVersion();
int fnLDA_GetDeviceStatus(unsigned int deviceID);

int fnLDA_SetChannel(unsigned int deviceID, int channel);

int fnLDA_SetWorkingFrequency(unsigned int deviceID, int frequency);

int fnLDA_SetAttenuation(unsigned int deviceID, int attenuation);
int fnLDA_SetAttenuationHR(unsigned int deviceID, int attenuation);
int fnLDA_SetAttenuationHRQ(unsigned int deviceID, int attenuation, int channel);

int fnLDA_SetRampStart(unsigned int deviceID, int rampstart);
int fnLDA_SetRampStartHR(unsigned int deviceID, int rampstart);
int fnLDA_SetRampEnd(unsigned int deviceID, int rampstop);
int fnLDA_SetRampEndHR(unsigned int deviceID, int rampstop);
int fnLDA_SetAttenuationStep(unsigned int deviceID, int attenuationstep);
int fnLDA_SetAttenuationStepHR(unsigned int deviceID, int attenuationstep);
int fnLDA_SetAttenuationStepTwo(unsigned int deviceID, int attenuationstep2);
int fnLDA_SetAttenuationStepTwoHR(unsigned int deviceID, int attenuationstep2);

int fnLDA_SetDwellTime(unsigned int deviceID, int dwelltime);
int fnLDA_SetDwellTimeTwo(unsigned int deviceID, int dwelltime2);
int fnLDA_SetIdleTime(unsigned int deviceID, int idletime);
int fnLDA_SetHoldTime(unsigned int deviceID, int holdtime);

int fnLDA_SetProfileElement(unsigned int deviceID, int index, int attenuation);
int fnLDA_SetProfileElementHR(unsigned int deviceID, int index, int attenuation);
int fnLDA_SetProfileCount(unsigned int deviceID, int profilecount);
int fnLDA_SetProfileIdleTime(unsigned int deviceID, int idletime);
int fnLDA_SetProfileDwellTime(unsigned int deviceID, int dwelltime);
int fnLDA_StartProfile(unsigned int deviceID, int mode);

int fnLDA_SetRFOn(unsigned int deviceID, bool on);

int fnLDA_SetRampDirection(unsigned int deviceID, bool up);
int fnLDA_SetRampMode(unsigned int deviceID, bool mode);
int fnLDA_SetRampBidirectional(unsigned int deviceID, bool bidir_enable);
int fnLDA_StartRamp(unsigned int deviceID, bool go);

int fnLDA_SaveSettings(unsigned int deviceID);

int fnLDA_GetWorkingFrequency(unsigned int deviceID);
int fnLDA_GetMinWorkingFrequency(unsigned int deviceID);
int fnLDA_GetMaxWorkingFrequency(unsigned int deviceID);

int fnLDA_GetAttenuation(unsigned int deviceID);
int fnLDA_GetAttenuationHR(unsigned int deviceID);
int fnLDA_GetRampStart(unsigned int deviceID);
int fnLDA_GetRampStartHR(unsigned int deviceID);
int fnLDA_GetRampEnd(unsigned int deviceID);
int fnLDA_GetRampEndHR(unsigned int deviceID);

int fnLDA_GetDwellTime(unsigned int deviceID);
int fnLDA_GetDwellTimeTwo(unsigned int deviceID);
int fnLDA_GetIdleTime(unsigned int deviceID);
int fnLDA_GetHoldTime(unsigned int deviceID);

int fnLDA_GetAttenuationStep(unsigned int deviceID);
int fnLDA_GetAttenuationStepHR(unsigned int deviceID);
int fnLDA_GetAttenuationStepTwo(unsigned int deviceID);
int fnLDA_GetAttenuationStepTwoHR(unsigned int deviceID);
int fnLDA_GetRF_On(unsigned int deviceID);

int fnLDA_GetProfileElement(unsigned int deviceID, int index);
int fnLDA_GetProfileElementHR(unsigned int deviceID, int index);
int fnLDA_GetProfileCount(unsigned int deviceID);
int fnLDA_GetProfileDwellTime(unsigned int deviceID);
int fnLDA_GetProfileIdleTime(unsigned int deviceID);
int fnLDA_GetProfileIndex(unsigned int deviceID);

int fnLDA_GetMaxAttenuation(unsigned int deviceID);
int fnLDA_GetMaxAttenuationHR(unsigned int deviceID);
int fnLDA_GetMinAttenuation(unsigned int deviceID);
int fnLDA_GetMinAttenuationHR(unsigned int deviceID);
int fnLDA_GetMinAttenStep(unsigned int deviceID);
int fnLDA_GetMinAttenStepHR(unsigned int deviceID);

int fnLDA_GetFeatures(unsigned int deviceID);
