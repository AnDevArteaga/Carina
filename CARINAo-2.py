import time
import threading
import numpy as np
import matplotlib.pyplot as plt # For plotting

class SharedMemory:
    """Espacio de memoria compartida entre Object Level y Meta Level."""
    def __init__(self):
        self.memory = {}
        self._lock = threading.Lock()

    def update(self, key, value):
        with self._lock:
            self.memory[key] = value

    def read(self, key):
        with self._lock:
            return self.memory.get(key, None)

class ObjectLevel:
    """Nivel Cognitivo - Ejecuta funciones cognitivas y mantiene el modelo del mundo."""
    def __init__(self, shared_memory):
        self.shared_memory = shared_memory
        self.current_plan = []
        self.running = True
        self.start_time = self.shared_memory.read("start_time")

    def anytime_planning(self, goal):
        print(f"ObjectLevel: Starting anytime_planning for '{goal}'")
        iteration_count = 0
        # Increased max_iterations to allow more time for utility dynamics to play out
        max_iterations = 60 # e.g., for 30 seconds of planning if sleep is 0.5s

        while self.running and iteration_count < max_iterations:
            elapsed_time = time.time() - self.start_time
            new_step = f"Step {len(self.current_plan) + 1} towards {goal}"
            self.current_plan.append(new_step)
            current_quality = float(len(self.current_plan))

            history_qualities = self.shared_memory.read("performance_history_qualities") or []
            history_qualities.append(current_quality)
            self.shared_memory.update("performance_history_qualities", history_qualities)
            self.shared_memory.update("current_quality", current_quality)
            self.shared_memory.update("current_plan_length", len(self.current_plan))

            # print(f"ObjectLevel: Plan step {len(self.current_plan)}, Quality: {current_quality}, Time: {elapsed_time:.2f}s")
            time.sleep(0.5)
            iteration_count += 1
            if self.shared_memory.read("stop_signal"):
                print("ObjectLevel: Received stop signal.")
                self.running = False
                break
        print(f"ObjectLevel: Anytime planning stopped. Plan length: {len(self.current_plan)}")
        self.shared_memory.update("final_plan", self.current_plan)


class MetaLevel:
    """Nivel Metacognitivo - Supervisa y controla el Object Level."""
    def __init__(self, shared_memory):
        self.shared_memory = shared_memory
        self.model_of_the_self = {}
        self.plot_data = {
            "times": [],
            "qualities": [],
            "intrinsic_values": [],
            "time_costs": [],
            "total_utilities": [],
            "optimal_stop_time": None,
            "optimal_stop_utility": None,
            "optimal_stop_quality": None
        }
        self.start_time = self.shared_memory.read("start_time")
        self.object_level_running = True

    def calculate_utility_components(self, quality, time_elapsed):
        intrinsic_value = float(quality)
        # Increased time_cost_exponent_factor to make cost of time more significant
        time_cost_exponent_factor = 0.15 # << ADJUST THIS VALUE (e.g., 0.1, 0.15, 0.2)
        time_cost = np.exp(time_elapsed * time_cost_exponent_factor) - 1
        total_utility = intrinsic_value - time_cost
        return intrinsic_value, time_cost, total_utility

    def update_model_of_the_self(self):
        self.model_of_the_self["performance_history_qualities"] = self.shared_memory.read("performance_history_qualities")
        self.model_of_the_self["current_quality"] = self.shared_memory.read("current_quality")
        if self.shared_memory.read("stop_signal"):
            self.object_level_running = False

    def stop_reasoning(self):
        print("MetaLevel: Starting stop_reasoning monitoring.")
        monitoring_interval = 0.6
        
        # Small delay before stopping is allowed, to let curves develop
        minimum_run_time_before_stop = 2.0 # seconds

        while self.object_level_running:
            time.sleep(monitoring_interval)
            self.update_model_of_the_self()

            current_quality_val = self.model_of_the_self.get("current_quality")
            if current_quality_val is None:
                continue
            
            current_quality = float(current_quality_val)
            elapsed_time = time.time() - self.start_time

            # Simplified projection for MPVC: assume a small constant improvement for next step
            projected_quality_next_step = current_quality + 0.5 # (Quality gain per monitoring_interval)

            intrinsic_now, cost_now, utility_now = self.calculate_utility_components(current_quality, elapsed_time)
            _ , _ , utility_future = self.calculate_utility_components(projected_quality_next_step, elapsed_time + monitoring_interval)

            self.plot_data["times"].append(elapsed_time)
            self.plot_data["qualities"].append(current_quality)
            self.plot_data["intrinsic_values"].append(intrinsic_now)
            self.plot_data["time_costs"].append(cost_now)
            self.plot_data["total_utilities"].append(utility_now)
            
            print(f"MetaLevel: Time: {elapsed_time:.2f}s, Q: {current_quality:.1f}, U_now: {utility_now:.2f}, U_future: {utility_future:.2f}, Cost: {cost_now:.2f}")

            # Stop if projected utility is not better AND we've run for a minimum duration
            if utility_future <= utility_now and elapsed_time > minimum_run_time_before_stop:
                print(f"MetaLevel: Stop Reasoning. U_future ({utility_future:.2f}) <= U_now ({utility_now:.2f}) at t={elapsed_time:.2f}s.")
                self.shared_memory.update("stop_signal", True)
                self.plot_data["optimal_stop_time"] = elapsed_time
                self.plot_data["optimal_stop_utility"] = utility_now
                self.plot_data["optimal_stop_quality"] = current_quality
                self.object_level_running = False
                break
            
            if not self.shared_memory.read("object_level_running_flag"):
                 print("MetaLevel: Object level seems to have stopped independently.")
                 self.object_level_running = False
                 if self.plot_data["optimal_stop_time"] is None and self.plot_data["times"]:
                    self.plot_data["optimal_stop_time"] = self.plot_data["times"][-1]
                    self.plot_data["optimal_stop_utility"] = self.plot_data["total_utilities"][-1]
                    self.plot_data["optimal_stop_quality"] = self.plot_data["qualities"][-1]
                 break

        print("MetaLevel: Monitoring stopped.")
        self.shared_memory.update("plot_data_final", self.plot_data)


class CARINA:
    def __init__(self):
        self.shared_memory = SharedMemory()
        self.shared_memory.update("start_time", time.time())
        self.shared_memory.update("stop_signal", False)
        self.shared_memory.update("performance_history_qualities", [])
        self.shared_memory.update("object_level_running_flag", True)

        self.object_level = ObjectLevel(self.shared_memory)
        self.meta_level = MetaLevel(self.shared_memory)

    def execute(self, goal):
        print(f"CARINA: Executing goal '{goal}'")
        self.shared_memory.update("goal", goal)

        planning_thread = threading.Thread(target=self.object_level.anytime_planning, args=(goal,))
        monitoring_thread = threading.Thread(target=self.meta_level.stop_reasoning)

        planning_thread.start()
        monitoring_thread.start()

        planning_thread.join()
        print("CARINA: Planning thread joined.")
        self.shared_memory.update("object_level_running_flag", False)

        monitoring_thread.join()
        print("CARINA: Monitoring thread joined.")

        final_plan = self.shared_memory.read("final_plan")
        plot_data = self.shared_memory.read("plot_data_final")
        return final_plan, plot_data

def plot_utility_vs_time(plot_data):
    if not plot_data or not plot_data["times"]:
        print("No data to plot.")
        return

    times = np.array(plot_data["times"])
    # Ensure all plot data arrays are of the same length before plotting
    min_len = len(times)
    intrinsic_values = np.array(plot_data["intrinsic_values"][:min_len])
    time_costs = np.array(plot_data["time_costs"][:min_len])
    total_utilities = np.array(plot_data["total_utilities"][:min_len])


    plt.figure(figsize=(10, 7)) # Slightly taller for better annotation space

    plt.plot(times, intrinsic_values, label='Intrinsic Value Function (Quality)', color='green', linestyle='-', linewidth=2)
    plt.plot(times, time_costs, label='Cost of Time (Magnitude)', color='red', linestyle=':', linewidth=2)
    plt.plot(times, total_utilities, label='Time-Dependent Utility (Net)', color='blue', linewidth=2.5)

    optimal_time = plot_data.get("optimal_stop_time")
    optimal_utility = plot_data.get("optimal_stop_utility")

    if optimal_time is not None and optimal_utility is not None:
        plt.scatter([optimal_time], [optimal_utility], color='black', s=120, zorder=5, label='Optimal Stopping Point', marker='X')
        plt.vlines(optimal_time, min(0, np.min(total_utilities) if total_utilities.size > 0 else 0), optimal_utility, colors='dimgray', linestyles='dashdot', zorder=0)
        plt.hlines(optimal_utility, 0, optimal_time, colors='dimgray', linestyles='dashdot', zorder=0)
        
        optimal_quality_at_stop = plot_data.get("optimal_stop_quality", "N/A")
        annotation_text = (f"Stop Point\n"
                           f"Time: {optimal_time:.2f}s\n"
                           f"Net Utility: {optimal_utility:.2f}\n"
                           f"Quality: {optimal_quality_at_stop:.1f}")
        
        # Adjust annotation position dynamically
        text_x_offset = (times.max() - times.min()) * 0.05 # 5% of x-range
        text_y_offset = (max(np.max(intrinsic_values), np.max(total_utilities)) - min(0, np.min(total_utilities))) * 0.05 # 5% of y-range
        
        # Heuristic for placing annotation to avoid overlap
        if optimal_time > times.mean(): # If stopping point is in the right half
            annot_x = optimal_time - text_x_offset
            ha = 'right'
        else: # If stopping point is in the left half
            annot_x = optimal_time + text_x_offset
            ha = 'left'

        if optimal_utility > total_utilities.mean(): # If stopping point is in the upper half
             annot_y = optimal_utility - text_y_offset
             va = 'top'
        else:
             annot_y = optimal_utility + text_y_offset
             va = 'bottom'


        plt.annotate(annotation_text,
                     xy=(optimal_time, optimal_utility),
                     xytext=(annot_x, annot_y),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                     bbox=dict(boxstyle="round,pad=0.5", fc="ivory", ec="gray", alpha=0.9),
                     fontsize=9,
                     ha=ha, va=va)

    plt.xlabel('Time (seconds)')
    plt.ylabel('Utility')
    plt.title('Meta-Level Control: Utility Dynamics Over Time', fontsize=14)
    plt.legend(loc='best')
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Adjust y-limits to ensure visibility of curves, especially if utility goes negative
    y_min_plot = min(0, np.min(total_utilities) if total_utilities.size > 0 else 0, np.min(time_costs) if time_costs.size > 0 else 0)
    y_max_plot = max(np.max(intrinsic_values) if intrinsic_values.size > 0 else 1, np.max(total_utilities) if total_utilities.size > 0 else 1)
    plt.ylim(y_min_plot - abs(y_min_plot*0.1) - 1, y_max_plot + abs(y_max_plot*0.1) +1) # Add some padding
    
    plt.axhline(0, color='black', linewidth=0.5, linestyle='-') # X-axis line
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    tutor_mind = CARINA()
    goal = "Aprender funciones exponenciales en IA" # More specific goal
    final_plan, collected_plot_data = tutor_mind.execute(goal)

    print("\n--- Execution Finished ---")
    if final_plan:
        print(f"Final plan ({len(final_plan)} steps):")
        # for i, step in enumerate(final_plan):
        #     print(f"  {i+1}. {step}")
    else:
        print("No final plan generated.")

    if collected_plot_data and collected_plot_data["times"]:
        plot_utility_vs_time(collected_plot_data)
    else:
        print("No plot data collected or data is empty.")