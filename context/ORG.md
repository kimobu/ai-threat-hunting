# Company
Dunder Mifflin (DM) is a mid-sized paper retailer in the northeast United States.
Due to budget cuts they have minimal IT support leaving many issues unpatched or unaddressed.

# Network
The DM network consists of Windows Active Directory domains DUNDERMIFFLIN.LOCAL, NORTH.DUNDERMIFFLIN.LOCAL, and their newly acquired subsidiary SABRE.LOCAL.
Most computers run a version of Microsoft Windows. User workstations run Windows 10 or 11. Servers include Windows 2012 R2, Windows 2016, and Windows 2019.
The network also includes an Ubuntu Linux web server and a macOS workstation. 

# Security 
DM uses Security Onion to provide security visibility. 
A network tap provides east/west and north/south network traffic inspection. It does not perform TLS inspection.
Elastic Agent is installed on most systems to provide host endpoint detection and response.
Powershell is logged and collected by Elastic Agent..