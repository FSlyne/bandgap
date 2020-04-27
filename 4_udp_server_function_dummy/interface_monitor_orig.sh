#!/bin/bash
#
# Number of seconds to average data over
avgsecs=3

if [ "$1" == "" ]; then
                echo "Usage: $0 <interface>" >&2
                echo "" >&2
                echo "Available interfaces:" >&2
                cat /proc/net/dev |cut -f1 -d':' |tail -n'+3' >&2
                exit 99
fi

# Use two arrays to store history of rx/tx total bytes transferred
declare -a hist_rx hist_tx

# Print interface name at the top
# echo "$1:"

rm usage_$1.log

QOS_LEVEL=1

while [ 1 ]; do

                # Trim arrays to last $avgsecs secs
                while [ ${#hist_rx[*]} -gt $avgsecs ]; do
                                unset hist_rx[0]
                                hist_rx=("${hist_rx[@]}")
                done
                while [ ${#hist_tx[*]} -gt $avgsecs ]; do
                                unset hist_tx[0]
                                hist_tx=("${hist_tx[@]}")
                done

                # Get total transferred bytes
                rx_bytes_last=$rx_bytes
                tx_bytes_last=$tx_bytes
                rx_bytes=$(cat /proc/net/dev |grep "$1:" |cut -f2 -d':' |awk '{print $1}')
                tx_bytes=$(cat /proc/net/dev |grep "$1:" |cut -f2 -d':' |awk '{print $9}')

                # Skip output if this is the first run
                [ -z $rx_bytes_last ] && sleep 1 && continue

                # Calculate diff from previous run
                hist_rx[${#hist_rx[*]}]=$(($rx_bytes - $rx_bytes_last))
                hist_tx[${#hist_tx[*]}]=$(($tx_bytes - $tx_bytes_last))

                # Calculate RX average
                rx_sum=0
                for i in "${hist_rx[@]}"; do rx_sum=$(($rx_sum + $i)); done
                rx_avg=$((rx_sum / ${#hist_rx[*]}))

                # Calculate TX average
                tx_sum=0
                for i in "${hist_tx[@]}"; do tx_sum=$(($tx_sum + $i)); done
                tx_avg=$((tx_sum / ${#hist_tx[*]}))

		echo `date +'%Y-%m-%d %H:%M:%S'` $tx_avg $rx_avg >> usage_$1.log

		# Hysteresis !!!
		if [[ ( "$QOS_LEVEL" == 1 ) && ( "$tx_avg" > 1900000 ) ]] ; then
	            QOS_LEVEL=2
		    echo `date +'%Y-%m-%d %H:%M:%S'` Setting QoS to $QOS_LEVEL $tx_avg $rx_avg
	            # Run ABNO bash script
	        elif [[ ( "$QOS_LEVEL" == 2 ) && ( "$tx_avg" > 15000000 ) ]] ; then
                    QOS_LEVEL=3
		    echo `date +'%Y-%m-%d %H:%M:%S'` Setting QoS to $QOS_LEVEL $tx_avg $rx_avg
                    # Run ABNO bash script for QoS 3
                elif [[ ( "$QOS_LEVEL" == 3 ) && ( "$tx_avg" > 19000000 ) ]] ; then
                    QOS_LEVEL=4
		    echo `date +'%Y-%m-%d %H:%M:%S'` Setting QoS to $QOS_LEVEL $tx_avg $rx_avg
                    # Run ABNO bash script for QoS 4
                elif [[ ( "$QOS_LEVEL" == 4 ) && ( "$tx_avg" < 18500000 ) ]] ; then
                    QOS_LEVEL=3
                    # Run ABNO bash script for QoS 3
		    echo `date +'%Y-%m-%d %H:%M:%S'` Setting QoS to $QOS_LEVEL $tx_avg $rx_avg
                elif [[ ( "$QOS_LEVEL" == 3 ) && ( "$tx_avg" < 14500000 ) ]] ; then
                    QOS_LEVEL=2
		    echo `date +'%Y-%m-%d %H:%M:%S'` Setting QoS to $QOS_LEVEL $tx_avg $rx_avg
                    # Run ABNO bash script for QoS 2
                elif [[ ( "$QOS_LEVEL" == 2 ) && ( "$tx_avg" < 1800000 ) ]] ; then
                    QOS_LEVEL=1
		    echo `date +'%Y-%m-%d %H:%M:%S'` Setting QoS to $QOS_LEVEL $tx_avg $rx_avg
                    # Run ABNO bash script for QoS 2
                fi

                # Convert values to kilobytes/sec
                rx_val=$(($rx_avg / 1024))
                rx_unit="KB/s"
                tx_val=$(($tx_avg / 1024))
                tx_unit="KB/s"

                # Convert values to megabytes/sec (if >1MB)
                if [ $rx_avg -gt 1048576 ]; then
                        rx_val=$(($rx_val / 1024))
                        rx_unit="MB/s"
                fi
                if [ $tx_avg -gt 1048576 ]; then
                        tx_val=$(($tx_val / 1024))
                        tx_unit="MB/s"
                fi

                # Output data
                printf "\r    rx: %3d %4s, tx: %3d %4s" $rx_val $rx_unit $tx_val $tx_unit

                sleep 1
done


