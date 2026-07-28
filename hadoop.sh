#!/bin/bash

clear

RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
BLUE="\e[34m"
CYAN="\e[36m"
MAGENTA="\e[35m"
WHITE="\e[97m"
RESET="\e[0m"

source ~/.bashrc 2>/dev/null

echo -e "${CYAN}"
echo "======================================================"
echo "                 HADOOP INSTALLER"
echo "======================================================"
echo -e "${RESET}"

echo -e "${GREEN}Developer : Niranjan Kumar K${RESET}"
echo -e "${YELLOW}Version   : 2.0 ${RESET}"
echo -e "${BLUE}Installing and configuring Hadoop ...${RESET}"
echo

HADOOP_VERSION="3.4.2"
HADOOP_DIR="$HOME/hadoop"

echo -e "${CYAN}[1/8] Checking Java...${RESET}"
java -version >/dev/null 2>&1 || {
    echo -e "${RED}Java not found! Please install Java first.${RESET}"
    exit 1
}

JAVA_HOME=$(dirname "$(dirname "$(readlink -f "$(which java)")")")

echo -e "${CYAN}[2/8] Setting up SSH key for localhost...${RESET}"
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa >/dev/null 2>&1
fi
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys

echo -e "${CYAN}[3/8] Downloading Hadoop...${RESET}"
wget -q --show-progress -c "https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz"

echo -e "${CYAN}[4/8] Extracting Hadoop...${RESET}"
tar -xzf "hadoop-${HADOOP_VERSION}.tar.gz"
rm -rf "$HADOOP_DIR"
mv "hadoop-${HADOOP_VERSION}" "$HADOOP_DIR"
rm -f "hadoop-${HADOOP_VERSION}.tar.gz"

echo -e "${CYAN}[5/8] Configuring environment variables...${RESET}"
grep -q "HADOOP_HOME" ~/.bashrc || cat >> ~/.bashrc <<EOF

# Hadoop Environment Variables
export JAVA_HOME=$JAVA_HOME
export HADOOP_HOME=$HADOOP_DIR
export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin
EOF

export HADOOP_HOME=$HADOOP_DIR
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

sed -i "s|^export JAVA_HOME=.*|export JAVA_HOME=$JAVA_HOME|" "$HADOOP_HOME/etc/hadoop/hadoop-env.sh" 2>/dev/null || true

echo -e "${CYAN}[6/8] Configuring XML cluster files...${RESET}"
mkdir -p "$HOME/hdfs/namenode"
mkdir -p "$HOME/hdfs/datanode"

cat > "$HADOOP_HOME/etc/hadoop/core-site.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
EOF

cat > "$HADOOP_HOME/etc/hadoop/hdfs-site.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file://$HOME/hdfs/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file://$HOME/hdfs/datanode</value>
    </property>
</configuration>
EOF

cat > "$HADOOP_HOME/etc/hadoop/mapred-site.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>\$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/*:\$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/*</value>
    </property>
</configuration>
EOF

cat > "$HADOOP_HOME/etc/hadoop/yarn-site.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.env-whitelist</name>
        <value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_MAPRED_HOME</value>
    </property>
</configuration>
EOF

echo -e "${CYAN}[7/8] Formatting NameNode...${RESET}"
"$HADOOP_HOME/bin/hdfs" namenode -format -force >/dev/null 2>&1

echo -e "${CYAN}[8/8] Verifying installation...${RESET}"
"$HADOOP_HOME/bin/hadoop" version | head -n 2

echo
echo -e "${GREEN}=============================================="${RESET}
echo -e "${GREEN}     Hadoop Setup Completed Successfully!     "${RESET}
echo -e "${GREEN}=============================================="${RESET}
echo
echo -e "${WHITE}Developer   : Niranjan Kumar K${RESET}"
echo -e "${WHITE}HADOOP_HOME : $HADOOP_HOME${RESET}"
echo -e "${WHITE}JAVA_HOME   : $JAVA_HOME${RESET}"
echo

echo -e "${CYAN}=============================================="${RESET}
echo -e "${YELLOW}                 HOW TO USE                   "${RESET}
echo -e "${CYAN}=============================================="${RESET}
echo
echo -e "${WHITE}1. Load updated environment variables:${RESET}"
echo -e "   ${GREEN}source ~/.bashrc${RESET}"
echo
echo -e "${WHITE}2. Start Hadoop Services:${RESET}"
echo -e "   ${GREEN}start-dfs.sh${RESET}"
echo -e "   ${GREEN}start-yarn.sh${RESET}"
echo
echo -e "${WHITE}3. Verify Running Daemons:${RESET}"
echo -e "   ${GREEN}jps${RESET}"
echo -e "   (You should see: NameNode, DataNode, SecondaryNameNode, ResourceManager, NodeManager)"
echo
echo -e "${WHITE}4. Access Web Interfaces in Web Browser:${RESET}"
echo -e "   • NameNode (HDFS)    : ${BLUE}http://localhost:9870${RESET}"
echo -e "   • YARN ResourceManager: ${BLUE}http://localhost:8088${RESET}"
echo
echo -e "${WHITE}5. Stop Services (when done):${RESET}"
echo -e "   ${GREEN}stop-yarn.sh${RESET}"
echo -e "   ${GREEN}stop-dfs.sh${RESET}"
echo
echo -e "${MAGENTA}Thank you for using this installer!${RESET}"
