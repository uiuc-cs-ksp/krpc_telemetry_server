FROM node:latest

RUN useradd -ms /bin/bash nodeuser

USER nodeuser
RUN cd /home/nodeuser && \
git clone https://github.com/uiuc-cs-ksp/openmct-krpc-telemetry.git && \
git clone https://github.com/uiuc-cs-ksp/krpc_openmct_telemetry_server.git && \
cd openmct-krpc-telemetry && npm install

CMD cd /home/nodeuser/openmct-krpc-telemetry && npm start
