"""
Real-world testing integration for the RL filling control system.
Handles communication with physical device and data collection.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from tcp_client import TCPClient
from tcp_client import UDPClient
from modbus_client import ModbusClient
from file_handler import FileHandler
from real_data_processor import RealDataProcessor
from database_handler import DatabaseHandler
from reward_calculator import RewardCalculator
from config import (
    DEFAULT_UDP_IP, DEFAULT_UDP_PORT, DEFAULT_MODBUS_IP, DEFAULT_MODBUS_PORT,
    DEFAULT_MODBUS_REGISTER, DEFAULT_DB_CONFIG, DEFAULT_SAFE_WEIGHT_MIN, 
    DEFAULT_SAFE_WEIGHT_MAX, DEFAULT_WEIGHT_QUANTIZATION_STEP
)


class RealWorldTester:
    """Handles real-world testing with physical filling device."""
    
    def __init__(self,
                 udp_ip: str = DEFAULT_UDP_IP,
                 udp_port: int = DEFAULT_UDP_PORT,
                 modbus_ip: str = DEFAULT_MODBUS_IP,
                 modbus_port: int = DEFAULT_MODBUS_PORT,
                 modbus_register: int = DEFAULT_MODBUS_REGISTER,

                 quantization_step: int = DEFAULT_WEIGHT_QUANTIZATION_STEP,
                 db_config: Dict[str, Any] = None,
                 reward_calculator: Optional[RewardCalculator] = None):
        """
        Initialize real-world tester.
        
        Args:
            tcp_ip: TCP server IP address
            tcp_port: TCP server port
            modbus_ip: Modbus device IP address
            modbus_port: Modbus device port
            modbus_register: Modbus register for switching points
            quantization_step: Weight quantization step
            db_config: Database configuration
            reward_calculator: Reward calculator instance
        """
        # Communication clients
        self.udp_client = UDPClient(udp_ip, udp_port)
        self.modbus_client = ModbusClient(modbus_ip, modbus_port, modbus_register)
        self.file_handler = FileHandler()
        
        # Data processing (use common weight limits scaled for real device)
        real_tolerance_limits = [
            DEFAULT_SAFE_WEIGHT_MIN * quantization_step,
            DEFAULT_SAFE_WEIGHT_MAX * quantization_step
        ]
        self.data_processor = RealDataProcessor(
            real_tolerance_limits,
            quantization_step
        )
        
        # Database handler
        self.db_handler = DatabaseHandler(db_config or DEFAULT_DB_CONFIG)
        
        # Reward calculator
        self.reward_calculator = reward_calculator or RewardCalculator()
        
        # Statistics
        self.session_stats = {
            'total_episodes': 0,
            'successful_episodes': 0,
            'failed_episodes': 0,
            'safe_episodes': 0,
            'overflow_episodes': 0,
            'underflow_episodes': 0
        }
        
    def connect_devices(self) -> bool:
        """
        Connect to all devices.
        
        Returns:
            True if all connections successful, False otherwise
        """
        logging.info("Connecting to devices...")
        
        udp_connected = self.udp_client.connect()
        modbus_connected = self.modbus_client.connect()
       # db_connected = self.db_handler.connect()
        
        if udp_connected and modbus_connected:
            logging.info("All communication devices connected successfully")
            if False:
                logging.warning("Database connection failed - episodes will not be saved")
            return True
        else:
            logging.error("Failed to connect to devices")
            return False
    
    def run_episode(self) -> Optional[Dict[str, Any]]:
        """
        Run a single filling episode with the given switching point.
        
        Args:
            switching_point: Switching point to send to device
            
        Returns:
            Episode data dictionary or None if failed
        """
        logging.info(f"Starting episode with switching point: {"switching_point"}")
        
        # Send switching point to device
        #if not self.modbus_client.send_switching_point(switching_point):
        #    logging.error("Failed to send switching point")
        #    self.session_stats['failed_episodes'] += 1
        #    return None
        
        # Wait for episode to complete and receive data
        while True: 
            #raw_data = self.udp_client.receive_data()
            raw_data = "1,    1;-   598,80955;-   611,    1;-   640,    2;-   667,    2;-   667,    0;-   644,    2;-   629,    1;-   598,    3;-   578,    2;-   581,    0;-   581,    0;-   581,    0;-   581,    0;-   581,    0;-   581,    0;-   581,    0;-   594,    1;-   594,    0;-   607,    1;-   612,    0;-   619,    0;-   645,    2;-   671,    2;-   676,    0;-   673,    0;-   673,    0;-   679,    0;-   701,    2;-   717,    1;-   726,    0;-   862,   13;-   929,    6;-  1009,    8;-  1024,    1;-  1060,    3;-  1085,    2;-  1204,   11;-  1204,    0;-  1204,    0;-  1204,    0;-  1204,    0;-  1204,    0;-  1172,    3;-  1058,   11;-   554,   50;   259,   81;  1670,  141;  3262,  159;  5176,  191;  7209,  203;  9579,  237; 12350,  277; 15614,  326; 19307,  369; 23252,  394; 27419,  416; 31600,  418; 35996,  439; 40501,  450; 45333,  483; 50211,  487; 55019,  480; 59487,  446; 63623,  413; 67573,  395; 71467,  389; 75494,  402; 79404,  391; 83198,  379; 86602,  340; 89816,  321; 92988,  317; 96442,  345;100245,  380;104166,  392;107921,  375;111252,  333;114418,  316;117665,  324;121343,  367;125348,  400;129424,  407;133151,  372;136508,  335;139727,  321;143143,  341;147048,  390;151116,  406;155045,  392;158450,  340;161470,  302;164519,  304;168019,  350;172052,  403;176263,  421;180271,  400;183713,  344;186858,  314;190141,  328;193823,  368;197901,  407;201948,  404;205560,  361;208780,  322;212001,  322;215717,  371;219993,  427;224475,  448;228629,  415;232190,  356;235418,  322;238739,  332;242564,  382;246714,  415;250869,  415;254796,  392;258477,  368;262264,  378;266308,  404;270555,  424;274658,  410;278441,  378;281989,  354;285583,  359;289494,  391;293559,  406;297577,  401;301309,  373;304931,  362;308729,  379;312813,  408;317088,  427;321111,  402;324738,  362;328026,  328;331496,  347;335477,  398;339889,  441;344478,  458;348586,  410;352182,  359;355576,  339;359150,  357;363188,  403;367373,  418;371372,  399;374939,  356;378310,  337;381948,  363;386018,  407;390483,  446;394801,  431;398700,  389;402177,  347;405466,  328;409104,  363;413187,  408;417642,  445;422136,  449;426467,  433;430637,  417;434649,  401;438719,  407;442716,  399;446626,  391;450497,  387;454306,  380;458265,  395;462209,  394;    30,   30;462209,44376;466032,  382;469669,  363;473096,  342;476636,  354;480433,  379;484633,  420;489029,  439;493320,  429;497399,  407;501208,  380;505123,  391;509247,  412;513553,  430;517888,  433;521779,  389;525360,  358;528932,  357;532891,  395;537573,  468;542530,  495;547380,  485;551458,  407;554744,  328;557825,  308;561078,  325;565282,  420;570170,  488;575336,  516;580292,  495;584499,  420;588413,  391;592134,  372;596025,  389;600219,  419;604280,  406;608330,  405;611921,  359;615125,  320;617890,  276;620028,  213;622080,  205;623711,  163;625154,  144;626290,  113;626868,   57;627336,   46;627534,   19;627534,    0;627534,    0;627534,    0;627534,    0;627534,    0;626783,   75;626691,    9;626691,    0;626691,    0;626691,    0;626691,    0;626806,   11;626807,    0;626830,    2;626989,   15;627572,   58;628466,   89;629388,   92;630247,   85;630785,   53;631162,   37;631509,   34;631941,   43;632676,   73;633568,   89;634574,  100;635511,   93;636218,   70;636775,   55;637161,   38;637599,   43;638198,   59;638945,   74;639794,   84;640472,   67;640909,   43;641107,   19;641278,   17;641710,   43;642426,   71;643362,   93;644155,   79;644568,   41;644610,    4;644649,    3;644750,   10;645345,   59;646276,   93;647307,  103;648082,   77;648551,   46;648829,   27;649192,   36;649881,   68;650841,   96;651925,  108;652875,   95;653563,   68;654081,   51;654528,   44;655112,   58;655940,   82;656895,   95;657840,   94;658582,   74;659009,   42;659244,   23;659503,   25;660016,   51;660822,   80;661755,   93;662596,   84;663109,   51;663358,   24;663574,   21;664008,   43;664836,   82;665880,  104;666888,  100;667609,   72;667939,   33;668120,   18;668419,   29;669025,   60;669912,   88;670864,   95;671671,   80;672220,   54;672639,   41;673083,   44;673665,   58;674390,   72;675097,   70;675641,   54;675965,   32;676164,   19;676422,   25;676921,   49;677637,   71;678405,   76;679102,   69;679555,   45;679837,   28;680105,   26;680445,   34;680983,   53;681662,   67;682366,   70;682983,   61;683439,   45;683810,   37;684190,   38;684721,   53;685424,   70;686216,   79;686992,   77;687583,   59;688028,   44;688409,   38;688816,   40;689404,   58;690056,   65;690653,   59;691125,   47;691382,   25;691574,   19;691836,   26;692250,   41;692859,   60;693518,   65;694119,   60;694603,   48;694954,   35;695250,   29;695564,   31;695955,   39;696422,   46;696966,   54;697558,   59;698112,   55;698644,   53;699141,   49;699608,   46;700113,   50;700613,   50;701119,   50;701641,   52;702149,   50;702726,   57;703382,   65;704085,   70;704813,   72;705463,   65;706010,   54;706495,   48;706998,   50;707636,   63;708386,   75;709171,   78;709807,   63;710178,   37;710352,   17;710465,   11;710765,   30;711340,   57;712097,   75;712908,   81;713550,   64;714008,   45;714400,   39;714851,   45;715500,   64;716272,   77;717020,   74;717639,   61;718102,   46;718552,   45;719095,   54;719772,   67;720513,   74;721174,   66;721698,   52;722093,   39;722475,   38;722956,   48;723541,   58;724183,   64;724752,   56;725207,   45;725649,   44;726138,   48;726749,   61;727478,   72;728151,   67;728696,   54;729087,   39;729342,   25;729649,   30;730100,   45;730728,   62;731490,   76;732198,   70;732768,   57;733154,   38;733401,   24;   300,  300;778273, 750000;  25,  603;"

            if not raw_data:
                logging.error("No data received for 5 seconds from device")
                #self.session_stats['failed_episodes'] += 1
                continue
            if raw_data: break
        
        logging.info(f"Received raw data: {raw_data[:100]}...")  # Log first 100 chars
        
        # Parse the data
        parsed_data = self.data_processor.parse_raw_data(raw_data)
        if not parsed_data:
            logging.error("Failed to parse received data")
            self.session_stats['failed_episodes'] += 1
            return None
        
        # Create filling session for reward calculation
        filling_session = self.data_processor.create_filling_session(parsed_data)
        if not filling_session:
            logging.error("Failed to create filling session")
            self.session_stats['failed_episodes'] += 1
            return None
        
        # Calculate reward
        reward = self.reward_calculator.calculate_reward(
            filling_session.episode_length,
            filling_session.final_weight,
            method="standard"  # Use standard reward calculation
        )
        
        # Add reward to parsed data
        parsed_data['reward'] = reward
        parsed_data['filling_session'] = filling_session
        
        # Update statistics
        self._update_session_stats(parsed_data)
        
        # Save to database if connected
        self._save_episode_to_database(parsed_data)
        
        logging.info(f"Episode completed - Final weight: {parsed_data['final_weight']}, "
                    f"Reward: {reward:.2f}")
        
        return parsed_data
    
    def _update_session_stats(self, episode_data: Dict[str, Any]) -> None:
        """Update session statistics."""
        self.session_stats['total_episodes'] += 1
        self.session_stats['successful_episodes'] += 1
        
        if episode_data['overflow_amount'] > 0:
            self.session_stats['overflow_episodes'] += 1
        elif episode_data['underflow_amount'] > 0:
            self.session_stats['underflow_episodes'] += 1
        else:
            self.session_stats['safe_episodes'] += 1
    
    def _save_episode_to_database(self, episode_data: Dict[str, Any]) -> None:
        """Save episode to database."""
        try:
            # Save original data
            original_id = self.db_handler.save_original_episode(
                episode_data['raw_data'],
                episode_data['coarse_time'],
                episode_data['fine_time'],
                episode_data['total_time'],
                episode_data['switching_point'],
                episode_data['overflow_amount'],
                episode_data['underflow_amount']
            )
            
            if original_id:
                # Save parsed data
                parsed_id = self.db_handler.save_parsed_episode(
                    original_id,
                    episode_data['weight_sequence'],
                    episode_data['coarse_time'],
                    episode_data['fine_time'],
                    episode_data['total_time'],
                    episode_data['switching_point'],
                    episode_data['overflow_amount'],
                    episode_data['underflow_amount']
                )
                
                if parsed_id:
                    # Update statistics
                    episode_stats = self.data_processor.get_episode_stats(episode_data)
                    self.db_handler.save_statistics(**episode_stats)
                    
                    logging.info(f"Episode saved to database (IDs: {original_id}, {parsed_id})")
                
        except Exception as e:
            logging.error(f"Error saving episode to database: {e}")
    
    def run_agent_testing(self, agent, logger) -> List[Dict[str, Any]]:
        """
        Run multiple episodes using an RL agent to select switching points.
        
        Args:
            agent: Trained RL agent
            num_episodes: Number of episodes to run
            initial_switch_point: Starting switch point (from DEFAULT_STARTING_SWITCH_POINT)
            
        Returns:
            List of episode data dictionaries
        """
        if not self.connect_devices():
            logging.error("Failed to connect to devices")
            return []

        try:
            episodes = []    
            episode_num = 1

            while True:
                logging.info(f"Running episode {episode_num}")
                
                # Run episode (steps 2-5: device filling, data reception, parsing, reward calculation)
                episode_data = self.run_episode()
                if episode_data:
                    current_switch_point = episode_data['weight_sequence'][episode_data['weight_sequence'].index(-1) -1]
                    # Step 6: Update agent with real-world episode data (exactly like training)
                    filling_session = episode_data['filling_session']
                    self._update_agent_with_episode(agent, filling_session, current_switch_point)
                    #TODO: save to db after upate agent to save q_table
                    # Determine termination type
                    final_weight = episode_data['final_weight']
                    if final_weight < self.reward_calculator.safe_weight_min * self.data_processor.quantization_step:
                        termination_type = "underweight"
                    elif final_weight > self.reward_calculator.safe_weight_max * self.data_processor.quantization_step:
                        termination_type = "overweight"
                    else:
                        termination_type = "safe"
                    
                    # Get model-selected next switching point (what agent thinks is best now)
                    model_selected_next_switch_point = agent.get_optimal_switch_point()
                    
                    # Select next action for next episode (may include exploration)
                    next_switch_point, exploration_flag = agent.select_action(model_selected_next_switch_point)
                    
                    # Determine explored switching point
                    explored_switch_point = next_switch_point if exploration_flag else None 
                    
                    # Console output matching training format EXACTLY
                    print(f"--- Episode {episode_num} ---")
                    print(f"Experienced Switching Point: {current_switch_point}")
                    print(f"Termination Type: {termination_type}")
                    print(f"Model-Selected Next Switching Point: {model_selected_next_switch_point}")
                    print(f"Explored Switching Point: {explored_switch_point}")
                    print()
                    
                    logging.info(f"Episode {episode_num + 1} completed - "
                                f"Final weight: {episode_data['final_weight']}, "
                                f"Reward: {episode_data['reward']:.2f}")
                    episode_data = {
                        'episode': episode_num + 1,
                        'episode_num': episode_num + 1,  # For compatibility with desired plot format
                        'switch_point': current_switch_point,
                        'model_selected_switching_point': model_selected_next_switch_point,
                        'explored_switching_point': explored_switch_point,
                        'episode_length': len(episode_data),
                        'final_weight': final_weight,
                        'termination_type': termination_type,
                        'exploration_rate': 0,
                        'q_value': agent.q_table.copy(),
                        'total_time': episode_data['total_time']
                    }

            
            

                    # Send switching point to device
                    self.modbus_client.send_switching_point(next_switch_point)
                    output_paths = logger.get_output_paths()
                    self.file_handler.write_to_text(agent.q_table, output_paths['q_values_path'])
                


                    episodes.append(episode_data)
                    # Update current switch point for next episode
                    current_switch_point = next_switch_point
                    episode_num += 1
           
                
        except KeyboardInterrupt:
            logging.info("Testing interrupted by user")
        except Exception as e:
            logging.error(f"Error during testing: {e}")
        finally:
            self.file_handler.write_qvalue_updates_to_excel(episodes, output_paths['excel_path'])
            self.disconnect_devices()
            self._print_session_summary()
            return episodes
        
    def run_manual_testing(self, switching_points: List[float]) -> List[Dict[str, Any]]:
        """
        Run episodes with manually specified switching points.
        
        Args:
            switching_points: List of switching points to test
            
        Returns:
            List of episode data dictionaries
        """
        if not self.connect_devices():
            logging.error("Failed to connect to devices")
            return []
        
        episodes = []
        
        try:
            for i, switching_point in enumerate(switching_points):
                logging.info(f"Running episode {i + 1}/{len(switching_points)} "
                           f"with switching point: {switching_point}")
                
                episode_data = self.run_episode(switching_point)
                if episode_data:
                    episodes.append(episode_data)
                else:
                    logging.warning(f"Episode {i + 1} failed")
                
                # Brief pause between episodes
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            logging.info("Testing interrupted by user")
        except Exception as e:
            logging.error(f"Error during testing: {e}")
        finally:
            self.disconnect_devices()
        
        self._print_session_summary()
        return episodes
    
    def _print_session_summary(self) -> None:
        """Print session statistics summary."""
        stats = self.session_stats
        logging.info("\n" + "="*50)
        logging.info("REAL-WORLD TESTING SESSION SUMMARY")
        logging.info("="*50)
        logging.info(f"Total Episodes: {stats['total_episodes']}")
        logging.info(f"Successful Episodes: {stats['successful_episodes']}")
        logging.info(f"Failed Episodes: {stats['failed_episodes']}")
        logging.info(f"Safe Episodes: {stats['safe_episodes']}")
        logging.info(f"Overflow Episodes: {stats['overflow_episodes']}")
        logging.info(f"Underflow Episodes: {stats['underflow_episodes']}")
        
        if stats['successful_episodes'] > 0:
            safe_rate = (stats['safe_episodes'] / stats['successful_episodes']) * 100
            logging.info(f"Safe Fill Rate: {safe_rate:.1f}%")
        
        logging.info("="*50)
    
    def _update_agent_with_episode(self, agent, filling_session, switching_point):
        """
        Update the RL agent with real-world episode data (step 6 of the testing loop).
        
        Args:
            agent: RL agent to update
            filling_session: FillingSession object from real episode
            switching_point: Switching point that was used
        """
        try:
            # Different agents need different update methods
            agent_type = type(agent).__name__
            
            if agent_type == "QLearningAgent":  # MAB agent
                # MAB: Direct Q-value update with episode reward
                episode_length = filling_session.episode_length
                final_weight = filling_session.final_weight
                reward = self.reward_calculator.calculate_reward(episode_length, final_weight, method="mab")
                agent._update_q_value(switching_point, reward)
                logging.info(f"MAB agent updated: Q({switching_point}) with reward {reward:.2f}")
                
            elif agent_type in ["MonteCarloAgent", "TDAgent", "StandardQLearningAgent"]:
                # MC/TD/Q-Learning: Episode-based learning using FillingSession
                episode_length, final_weight = agent.train_episode(switching_point)
                logging.info(f"{agent_type} updated with episode: length={episode_length}, weight={final_weight}")
                
            else:
                logging.warning(f"Unknown agent type: {agent_type}, skipping update")
                
        except Exception as e:
            logging.error(f"Error updating agent with episode: {e}")
            
        # Update exploration rate if decay is enabled
        if hasattr(agent, '_update_exploration_rate'):
            agent._update_exploration_rate()
            logging.debug(f"Exploration rate: {agent.exploration_rate:.3f}")
    
    def disconnect_devices(self) -> None:
        """Disconnect from all devices."""
        logging.info("Disconnecting from devices...")
        self.udp_client.close()
        self.modbus_client.close()
        self.db_handler.close()
        logging.info("All devices disconnected")