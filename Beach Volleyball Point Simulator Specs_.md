

# **Specification for a Probabilistic Beach Volleyball Point Simulation and Impact Analysis Application**

## **I. Executive Summary**

This report outlines the comprehensive specification for a novel application designed to simulate beach volleyball points. The primary objective is to provide a robust, probabilistic model that can accurately simulate individual rallies based on detailed input statistics for each team's fundamental skills, including reception, setting, serving, attacking, and defending. Beyond mere simulation, the application will perform a sophisticated analysis to identify and quantify the relative importance of these fundamental statistics in determining the probability of winning a point. This capability will offer unparalleled insights, allowing users to understand how improvements in specific skills, such as a percentage increase in perfect reception, can translate into a measurable growth in point win probability. The insights derived from this application will be invaluable for coaches, analysts, and players seeking to optimize training strategies, evaluate team compositions, and refine tactical approaches in beach volleyball.

## **II. Beach Volleyball Game Mechanics and Scoring System**

The accurate simulation of beach volleyball points necessitates a deep understanding of the sport's fundamental rules and rally progression. The application's core logic is built upon these established mechanics.

### **Rally Point Scoring System**

The application will strictly adhere to the modern rally point scoring system, which dictates that a point is scored on every rally, irrespective of which team served.1 This system represents a significant evolution from the older "side-out" scoring format, where points could only be earned by the serving team. The adoption of rally scoring has notably increased the pace and consistency of match times, making the game more dynamic and, importantly for simulation, more mathematically tractable.2  
The direct mapping of every rally to a point for one team inherently simplifies the probabilistic modeling required for the application. In contrast to side-out scoring, which introduces an additional layer of complexity by requiring a team to first win the serve before accumulating points, the rally point system allows the simulation model to focus directly on the probability of a team winning a rally. This simplification streamlines the design of the underlying Markov chain or Monte Carlo logic, making it more straightforward to implement and interpret. The reduced computational complexity contributes to a more efficient and faster simulation process.6

### **Game and Set Structure**

A beach volleyball match is typically played as the best of three sets. The first two sets are contested until one team reaches 21 points, provided they hold a minimum lead of two points. Should the score reach a 20-20 tie, play continues until a two-point advantage is achieved (e.g., 22-20, 23-21).5 The deciding third set, if necessary, is played to 15 points, with the same requirement for a two-point difference.5 An important contextual rule for full match simulations, though not directly impacting single point simulation, is the switching of sides by teams after every 7 points in sets 1 and 2, and every 5 points in set 3\. This rule is designed to ensure equitable playing conditions, accounting for environmental factors such as wind and sun.2

### **Rally Initiation and Progression**

Every rally in beach volleyball commences with a serve.2 The serving player must execute their shot from behind the end line.7 Following the serve, the receiving team is permitted a maximum of three contacts with the ball to return it over the net.2 A nuanced aspect of this rule is that simultaneous touches by two teammates are counted as two hits, with the sole exception of a block.8 Furthermore, a ball that is driven into the net can still be recovered, provided the team remains within its three-hit limit.8  
The "three-hit rule" imposes a fundamental sequence within a rally for the receiving team: Serve Reception (first hit), Set (second hit), and Attack (third hit). This sequence is not merely a rule but a critical determinant of rally flow. The success and quality of each subsequent action are highly dependent on the preceding one. For example, a poorly executed reception (first hit) severely restricts the options available for the set (second hit), which, in turn, constrains the effectiveness of the attack (third hit). This highlights a crucial causal chain: the quality of the serve influences the quality of the reception, which then impacts the quality of the set, ultimately determining the efficacy of the attack. A perfect pass, for instance, enables a setter to execute an optimal set, thereby maximizing the attacker's potential for a kill. Conversely, a poor pass often forces a predictable or difficult set, significantly reducing the probability of a successful attack.  
This inherent dependency necessitates that the simulation model incorporates conditional probabilities. The probability of an attack resulting in a kill, for example, should be conditional on the quality of the preceding set (e.g., the probability of a kill after a perfect set will be substantially higher than after a poor set). This requires a more granular representation of each fundamental's outcome, such as categorizing reception quality on a multi-point scale (e.g., 0-3 or 0-4 as detailed in 10), rather than a simple binary success/failure. This design choice ensures the simulation is significantly more realistic and capable of capturing the nuanced flow of a beach volleyball rally.

### **Point Scoring Conditions and Faults**

A point is awarded to a team whenever it wins a rally.2 This occurs under several conditions: if the defending team fails to successfully return the ball over the net, if the opposing team hits the ball out of the designated court boundaries, or if a player on the opposing team commits a fault.7 Common faults that result in a point for the opponent include stepping on or over the end line during a serve, hitting or serving the ball into the net, touching the net while the ball is in play, or illegally reaching over or under the net (with exceptions for blocking or follow-through).7

### **Serve Rotation and Rights**

The dynamics of serving rights are integral to the point progression. If the serving team wins a rally, they score a point, and the same player continues to serve for the next rally.8 Conversely, if the receiving team wins the rally, they not only score a point but also gain the right to serve. In this scenario, the player on the newly serving team who  
*did not* serve last time will be the one to serve next.1 This alternating serve mechanism is a fundamental component of the simulation's state management, influencing the starting conditions for each new rally.

## **III. Input Data Specification: Team Fundamental Statistics**

The accuracy and utility of the simulation application are directly dependent on the quality and granularity of the input data. This section defines the specific fundamental statistics required for each team, outlining their interpretation and calculation methods. These statistics will serve as the foundational parameters for the probabilistic model.

### **General Input Structure**

The application will accept input statistics for two competing teams, designated as Team A and Team B. For each team, these statistics will represent probabilities or efficiency ratings for various outcomes within each fundamental skill category. Given the 2v2 nature of beach volleyball, the model should ideally accommodate both individual player statistics (which can then be aggregated) and direct team-level statistical inputs, offering flexibility to the user.

### **Fundamental Skill Categories and Key Metrics**

To ensure a comprehensive and realistic simulation, the following fundamental skill categories and their associated key metrics are required:

* **Serve**: The initial action of every rally, crucial for putting pressure on the opponent.  
  * **Service Ace Percentage (ACE%)**: The proportion of serves that result in an immediate point for the serving team, such as an untouched court hit or an unreturnable pass.11  
  * **Service Error Percentage (SE%)**: The proportion of serves that result in a fault, including hitting the net, going out of bounds, a foot-fault, or serving out of rotation.11  
  * **Serve Success Rate (SSR)**: A more nuanced metric that quantifies the percentage of serves that force the opponent "out of system," limit their attacking options, or specifically target weak passers or zones. This metric captures the disruptive quality of a serve beyond just direct aces.10  
  * **Serve Win Percentage (SWP)**: This metric measures how often a team scores a point when a specific player is serving. It combines direct aces, points won from opponent errors forced by tough serves, and points won through effective defense following the serve.10  
* **Reception (Serve Receive)**: The first contact for the receiving team, critical for initiating a successful offense.  
  * **Pass Quality Rating (PQR)**: A vital metric, typically scaled from 0 to 3 or 0 to 4, that evaluates the quality of the serve reception.10  
    * **Perfect Pass (3/4)**: A reception that allows for all offensive options, including quick attacks and the involvement of multiple attackers.  
    * **Good Pass (2/3)**: A reception that limits some offensive options but still permits multiple attackers.  
    * **Poor Pass (1/2)**: A reception that forces a predictable set, often limiting the team to a single attacking option or an off-system play.  
    * **Reception Error / Overpass (0/1)**: A complete failure in reception, frequently leading to an immediate point for the serving team.10  
  * **Serve Reception Error Percentage (RE%)**: The percentage of served balls that are not successfully kept in play on the receiver's side of the net.12  
* **Setting**: The second contact, responsible for preparing the attack.  
  * **Assist Percentage (A%)**: The proportion of sets that directly lead to a kill by a teammate.11  
  * **Ball Handling Error Percentage (BHE%)**: The percentage of sets that result in a fault, such as a double hit, a thrown ball, or a lifted ball.11  
  * **Set Efficacy by Reception Quality**: This represents the probabilities of achieving specific set qualities (e.g., perfect, good, poor, error) given the quality of the preceding reception. This is crucial for accurately capturing the inter-skill dependencies within a rally.10  
  * **Preferred Attack Zone/Set Type Tendencies**: Probabilities of setting to particular attack zones or utilizing specific set types (e.g., quick, outside, back row, jump set vs. standing set) based on the quality of the pass and the setter's court position.10  
* **Attack**: The third contact, aimed at scoring a point.  
  * **Attack Kill Percentage (K%)**: The percentage of attack attempts that result in a point, either by being unreturnable or by directly leading to a blocking error by the opponent.11  
  * **Attack Error Percentage (E%)**: The percentage of attack attempts that result in a fault, such as hitting the ball out of bounds, into the net, being blocked down onto the attacker's side, or an illegal hit.11  
  * **Hitting Efficiency (ATT%)**: Calculated as (Kills \- Errors) / Total Attempts, this is a key measure of overall offensive effectiveness.11  
  * **First-Ball Kill Percentage (FBK%)**: Measures how often a team scores a point immediately after receiving serve, indicating offensive stability under pressure.10  
  * **Kill from Dig Transition Percentage**: Quantifies how effectively a team converts defensive plays (digs) into points through a subsequent counter-attack.10  
* **Defense (Block & Dig)**: Actions aimed at preventing the opponent from scoring.  
  * **Dig Percentage (DIG%)**: The percentage of attacked balls that are successfully passed and kept in play.11 This metric can be further refined by considering digging efficiency by zone and attack type.10  
  * **Block Kill Percentage (BLK\_K%)**: The percentage of blocks that result in an immediate point for the blocking team (also known as a terminal block).11  
  * **Controlled Block Percentage (CBLK%) / Positive Block Touch Percentage (PBT%)**: The percentage of blocks that, while not scoring a point directly, effectively slow down attacks, redirect them, or force the attacker to adjust. These actions create easier defensive opportunities for the blocking team.10  
  * **Blocking Error Percentage (BE%)**: The percentage of blocks that result in a fault by the blocking player, such as net contact or a centerline violation.11

### **Interconnectedness of Fundamental Statistics and the Necessity of Conditional Probabilities**

While individual metrics for each fundamental skill are important, a critical aspect of beach volleyball performance lies in the profound dependencies between these skills. Research consistently highlights that the outcome of one action significantly influences the efficacy of subsequent actions within a rally. For example, the quality of a serve reception has a direct predictive power over the outcome of the subsequent attack.15 Similarly, the characteristics of a serve technique are known to greatly influence the efficacy of the serve-reception, and poor serve-receptions are associated with a decrease in setting efficacy.13  
This reveals a clear, sequential causal chain within a rally: Serve Quality influences Reception Quality, which then impacts Set Quality, ultimately determining Attack Efficacy, and finally influencing Defensive Success. The success probability and quality of each subsequent action are not independent events but are conditional on the outcome and quality of the preceding action. A perfect pass, for instance, is a prerequisite for an optimal set, which in turn maximizes the probability of a successful attack.  
To accurately reflect this reality, the simulation model must incorporate conditional probabilities. For example, the probability of an attack resulting in a kill (P(Attack\_Kill)) must be conditional on the quality of the preceding set (Set\_Quality). This means that P(Attack\_Kill | Set\_Quality\_Perfect) will be significantly higher than P(Attack\_Kill | Set\_Quality\_Poor). This approach necessitates a more granular input data specification, potentially requiring distributions for quality ratings (e.g., P(Pass\_Quality\_0), P(Pass\_Quality\_1), P(Pass\_Quality\_2), P(Pass\_Quality\_3)) rather than just average success rates. The application will then utilize these distributions and conditional probabilities to model the rally flow accurately, leading to a much more dynamic and realistic simulation.

### **Beyond Simple Success Rates: The Value of Nuanced Metrics for Simulation Accuracy**

Beyond traditional "terminal" statistics that directly score points, such as "Aces" or "Kills" 11, advanced metrics offer deeper insights into game performance. Examples include "Serve Success Rate," which quantifies how often a serve forces an opponent "out of system" 10, "Pass Quality Rating" 10, and "Positive Block Touches".10 These nuanced metrics capture the  
*quality* and *enabling impact* of an action, not just its binary success or failure. For instance, a "controlled block" 14 or a "positive block touch" 10 may not result in an immediate point, but it significantly aids the team's subsequent defensive efforts by slowing down the attack or redirecting it to a more defensible area. Similarly, a "good pass" 10 is not perfect but still allows for multiple attacking options, which is a far more favorable outcome than a "poor pass" that forces a predictable offense.  
To create a truly realistic simulation, the input statistics should leverage these more detailed metrics. Instead of simply P(Serve\_Ace) and P(Serve\_Error), the application could take P(Serve\_Forces\_OOS\_Pass) or a distribution of P(Pass\_Quality\_X). This allows the simulation to model the *flow* and *quality* of the rally more accurately, as the quality of one action directly influences the probabilities of subsequent actions, rather than just ending the rally immediately. This approach makes the simulation more dynamic, provides a richer dataset for the importance analysis, and ultimately offers more granular insights into team performance.

### **Table 1: Key Beach Volleyball Fundamental Statistics and Definitions**

The following table provides a structured overview of the key fundamental statistics that will serve as input for the application, along with their definitions and calculation methods. This ensures a standardized and clear understanding for both data preparation and model implementation.

| Fundamental | Key Metric | Definition/Calculation | Source Snippets |
| :---- | :---- | :---- | :---- |
| **Serve** | Service Ace % (ACE%) | Percentage of serves that result directly in a point (e.g., untouched court, unreturnable pass). | 11 |
|  | Service Error % (SE%) | Percentage of serves that result in a fault (e.g., hitting net, out of bounds, foot-fault). | 11 |
|  | Serve Success Rate (SSR) | Percentage of serves that force opponent out of system, limit attacking options, or target weak passers/zones. | 10 |
| **Reception** | Pass Quality Rating (PQR) | A 0-3/0-4 scale evaluating reception quality: 3/4=Perfect (all options), 2/3=Good (limited options, multiple attackers), 1/2=Poor (predictable set), 0/1=Error/Overpass. | 10 |
|  | Serve Reception Error % (RE%) | Percentage of served balls not kept in play on receiver's side. | 12 |
| **Setting** | Assist % (A%) | Percentage of sets that lead to a kill. | 11 |
|  | Ball Handling Error % (BHE%) | Percentage of sets resulting in a fault (e.g., double hit, thrown ball, lifted ball). | 11 |
| **Attack** | Attack Kill % (K%) | Percentage of attack attempts that result in a point (unreturnable, leads to blocking error). | 11 |
|  | Attack Error % (E%) | Percentage of attack attempts that result in a fault (out of bounds, into net, blocked down). | 11 |
|  | Hitting Efficiency (ATT%) | (Kills \- Errors) / Total Attempts. | 11 |
| **Defense** | Dig % (DIG%) | Percentage of attacked balls successfully passed and kept in play. | 11 |
|  | Block Kill % (BLK\_K%) | Percentage of blocks that result in an immediate point (terminal block). | 11 |
|  | Controlled Block % (CBLK%) / Positive Block Touch % (PBT%) | Percentage of blocks that slow/redirect attacks, creating easier defensive opportunities. | 10 |

## **IV. Simulation Model Design**

The core of the application is a sophisticated probabilistic model that simulates the progression of beach volleyball points. This model is designed to reflect the dynamic and sequential nature of a rally.

### **Core Simulation Logic (Rally Flow)**

Each simulated rally commences with a serve from the designated serving team, determined by the current game state and the established serve rotation rules.2 The rally then progresses through a series of discrete states, which are modeled as a Markov chain.16 Each state represents a specific action within the rally and its associated efficacy or outcome. The transition from one state to the next is probabilistic, with probabilities derived from the input team statistics.  
The application of Markov chains is particularly well-suited for modeling the sequential, dependent actions in a beach volleyball rally. The "memoryless" property of a Markov chain, where the future state depends only on the current state and not the entire history, aligns perfectly with the rally's progression. This allows for dynamic transitions based on the quality of play; for instance, a "perfect reception" state leads to a higher probability of transitioning to an "in-system set" state, which then influences the "attack efficacy" state. This Markovian approach is superior to a simpler sequence of independent random draws, as it leads to a much more realistic, accurate, and insightful simulation of beach volleyball points.  
The rally flow within the simulation will follow these generalized states:

* **Serve (K0)**:  
  * **Initial State**: Serve\_Attempt\_Team\_X  
  * **Outcomes**: The serve can result in a Serve\_Ace\_Team\_X (point for serving team), a Serve\_Error\_Team\_X (point for receiving team), or the Serve\_In\_Play\_Received\_by\_Team\_Y. Probabilities for these outcomes are directly derived from the input Service Ace % and Service Error %.11  
* **Reception (KI \- first contact)**:  
  * **State**: Serve\_In\_Play\_Received\_by\_Team\_Y  
  * **Outcomes**: The reception can be categorized into Reception\_Perfect\_Team\_Y, Reception\_Good\_Team\_Y, Reception\_Poor\_Team\_Y, or a Reception\_Error\_Team\_Y (resulting in a point for the serving team). These probabilities are based on the input Pass Quality Rating distribution.10 The quality of this reception is critical, as it directly influences the quality of the subsequent set.13  
* **Set (KI \- second contact)**:  
  * **State**: Reception\_Quality\_Z\_Team\_Y (e.g., Reception\_Perfect\_Team\_Y)  
  * **Outcomes**: The set can be Set\_Perfect\_Team\_Y, Set\_Good\_Team\_Y, Set\_Poor\_Team\_Y, or a Set\_BallHandlingError\_Team\_Y (resulting in a point for Team X). The probabilities for these outcomes are conditional on the Reception\_Quality\_Z from the previous step.10  
* **Attack (KI \- third contact)**:  
  * **State**: Set\_Quality\_Q\_Team\_Y (e.g., Set\_Perfect\_Team\_Y)  
  * **Outcomes**: The attack can result in an Attack\_Kill\_Team\_Y (point for Team Y), an Attack\_Error\_Team\_Y (point for Team X), or the Attack\_In\_Play\_Defended\_by\_Team\_X. Probabilities are conditional on Set\_Quality\_Q and the team's Hitting Efficiency.11  
* **Defense/Block (KII, KIII, KIV, KV \- subsequent contacts)**:  
  * **State**: Attack\_In\_Play\_Defended\_by\_Team\_X  
  * **Outcomes**:  
    * **Block**: If the attack is blocked, outcomes include a Block\_Terminal\_Team\_X (point for Team X), a Block\_Controlled\_Team\_X (ball remains in play for Team X's defense), or a Block\_Error\_Team\_X (point for Team Y). Probabilities are based on Block Kill %, Controlled Block %, and Blocking Error %.10  
    * **Dig**: If the attack is not blocked, outcomes include a Dig\_Successful\_Team\_X (ball remains in play for Team X's offense) or a Dig\_Error\_Team\_X (point for Team Y). Probabilities are based on Dig %.11  
  * **Counter-Attack Cycle**: If the outcome is Block\_Controlled\_Team\_X or Dig\_Successful\_Team\_X, the rally transitions into a counter-attack sequence for Team X, repeating the Set \-\> Attack \-\> Defense/Block cycle until a point is scored.16

Any state where a point is scored (e.g., Serve\_Ace, Reception\_Error, Attack\_Kill, Block\_Terminal, Dig\_Error, Fault\_Net\_Touch) is considered an absorbing state, which signifies the end of the rally.16 If the receiving team wins the rally (e.g., via a  
Serve\_Error or an Attack\_Kill by Team Y), they gain the right to serve, and the serving player alternates for the next rally.1

### **Probabilistic Framework (Monte Carlo Simulation)**

The application will employ a Monte Carlo simulation approach to run multiple trials of beach volleyball points.19 For each action within a rally, a random number will be generated and compared against the defined probabilities (derived from input statistics) to determine the outcome. Input statistics, such as a Hitting Efficiency of.300, will be translated into probabilities for specific outcomes within the rally, often as  
*conditional probabilities* (e.g., P(Attack\_Kill | Set\_Quality\_X, Opponent\_Defense\_Y)). The model will logically infer these conditional probabilities from the provided input statistics. For instance, a higher Pass Quality Rating for a team will increase the probability of a Set\_Perfect, which in turn increases the P(Attack\_Kill) for that rally phase.

### **Incorporation of "Momentum"**

To enhance the realism of the simulation, the application can incorporate a "short-term momentum" or "hot hand" effect.20 This phenomenon suggests that winning consecutive points, particularly on serve, can slightly increase the probability of winning the  
*next* point on serve. This dynamic adjustment moves beyond the common assumption of independent and identically distributed (iid) points, which research indicates conflicts with observed psychological momentum in sports.20  
Momentum implies that a team's performance, specifically their probability of winning the next point on serve, is not static but can be dynamically influenced by recent success or failure. For example, winning several points in a row can boost confidence and performance, leading to a higher probability of winning the subsequent point, while a string of losses might have the opposite effect. Implementing parameters such as m1, m2, m3 (as described in 20) can represent the incremental boost in serve-winning probability after 1, 2, or 3 consecutive points won on serve. This adds a layer of sophistication that moves beyond purely statistical averages to capture the psychological and flow-based aspects inherent in competitive sports, making the simulation's output more reflective of actual match play. For the subsequent importance analysis, this means that the impact of a statistical improvement might be amplified or dampened by the current momentum state, providing a more nuanced understanding of skill importance.

### **Simulation Parameters**

The user will be able to define the **Number of Points to Simulate** (e.g., 1,000, 10,000, 100,000 points). A higher number of simulations increases the statistical reliability and accuracy of the probabilistic outcomes due to the law of large numbers inherent in Monte Carlo simulations.4 Additionally, the application will allow the user to specify a  
**Random Seed**. This feature ensures the reproducibility of simulation runs, which is critical for debugging, testing, and comparing results across different input parameter sets.

### **Table 2: Rally Action Probabilistic Outcomes (Example Flow)**

The following table illustrates a simplified example of how the application's simulation engine will translate input statistics into probabilistic outcomes at various stages of a rally. This clarifies the logical flow and the role of conditional probabilities.

| Current State/Action | Input Metric Used | Possible Outcomes | Probability/Distribution (Example) | Next State/Action |
| :---- | :---- | :---- | :---- | :---- |
| Serve Phase \- Team A serving | Team A Service Ace % (ACE%), Team A Service Error % (SE%) | Ace (Point for Team A) | P(Ace) \= 10% | Point for Team A |
|  |  | Error (Point for Team B) | P(Error) \= 15% | Point for Team B |
|  |  | In Play (Received by Team B) | P(In Play) \= 75% | Reception Phase \- Team B |
| Reception Phase \- Team B | Team B Pass Quality Rating (PQR) Distribution | Perfect Pass | P(Perfect Pass) \= 30% | Set Phase \- Team B (Perfect Pass) |
|  |  | Good Pass | P(Good Pass) \= 40% | Set Phase \- Team B (Good Pass) |
|  |  | Poor Pass | P(Poor Pass) \= 20% | Set Phase \- Team B (Poor Pass) |
|  |  | Reception Error (Point for Team A) | P(Reception Error) \= 10% | Point for Team A |
| Set Phase \- Team B (Perfect Pass) | Team B Set Efficacy by Reception Quality (Perfect Pass) | Perfect Set | P(Perfect Set | Perfect Pass) \= 90% | Attack Phase \- Team B (Perfect Set) |
|  |  | Good Set | P(Good Set | Perfect Pass) \= 8% | Attack Phase \- Team B (Good Set) |
|  |  | Ball Handling Error (Point for Team A) | P(BHE | Perfect Pass) \= 2% | Point for Team A |
| Attack Phase \- Team B (Perfect Set) | Team B Hitting Efficiency (ATT%) | Kill (Point for Team B) | P(Kill | Perfect Set) \= 60% | Point for Team B |
|  |  | Error (Point for Team A) | P(Error | Perfect Set) \= 15% | Point for Team A |
|  |  | Defended by Team A | P(Defended | Perfect Set) \= 25% | Defense/Block Phase \- Team A |

## **V. Statistical Importance Analysis**

A core requirement of the application is to determine which input statistics are most important for winning a point, providing a quantifiable and interpretable measure of their impact.

### **Goal of Analysis**

The primary goal of this analytical component is to quantify the marginal impact of each fundamental statistic on the probability of winning a point. This impact will be expressed in an easily interpretable format, such as "by receiving perfectly X% better, the probability of winning a point grows by Y%" \[User Query\]. This will enable users to prioritize skill development and strategic focus areas.

### **Methodology for Impact Quantification**

The most robust approach to quantifying the impact of various statistics involves a two-step process:

1. Large-Scale Monte Carlo Simulation for Data Generation:  
   The Monte Carlo point simulation will be executed for a very large number of points, ranging from 100,000 to 1,000,000, for a given set of team statistics. To generate a dataset suitable for subsequent regression or SHAP analysis, the simulation will be run multiple times with slight, systematic variations in the input statistics across different simulation runs. This process creates a synthetic dataset where the "independent variables" (input statistics) are intentionally varied, and the "dependent variable" (point win/loss outcome) is observed. This methodology is analogous to how advanced sports models run thousands of game simulations with adjusted parameters to understand their effects.4 For each simulated point, the win/loss outcome will be recorded, alongside the specific values of the input statistics that were used for that particular simulation run.  
2. Feature Importance Analysis on Simulated Data:  
   Once the large dataset of simulated points is generated, a feature importance analysis will be performed.  
   * **Logistic Regression**: A logistic regression model will be applied to this large dataset of simulated points.22 The dependent variable will be binary (Win=1, Loss=0 for a point), and the independent variables will be the input fundamental statistics (e.g., Serve Ace %, Pass Quality Rating, Hitting Efficiency %). The coefficients (or odds ratios) derived from the logistic regression will directly indicate the "feature importance" – how much each input statistic influences the log-odds of winning a point.22 A positive coefficient implies that an increase in that statistic increases the probability of winning. Odds ratios (e.g.,  
     e^coefficient) provide a multiplicative change in the odds of winning.22 Logistic regression is well-suited for binary outcomes 22 and can identify the simultaneous effect of multiple variables while accounting for potential confounding effects.24  
   * **SHAP (Shapley Additive Explanations) Values**: SHAP values, a concept rooted in cooperative game theory, offer a unified and fair measure of feature importance by quantifying the contribution of each input statistic to the model's prediction (the probability of winning a point).25 SHAP can be applied directly to the output of the simulation (treating the simulation itself as a "model") or to the logistic regression model trained on the simulated data. It explains  
     *why* a certain point was won or lost by attributing a portion of the predicted probability to each input feature. A significant advantage of SHAP values is their ability to provide a "fair" allocation of contribution among features, even when complex interactions exist.26 This is particularly beneficial over simple regression coefficients, which might not fully capture non-linear relationships or interdependencies. SHAP is also model-agnostic, meaning it can explain the output of any underlying simulation or predictive model.28 While computationally more intensive than simple regression for a very large number of features, sampling methods can approximate SHAP values 26, making it feasible for the defined set of fundamental statistics.

The most robust and comprehensive approach to fulfilling the user's requirement is this two-step methodology. First, a large-scale Monte Carlo simulation is run, not just for a single set of parameters, but with systematic variations in all input fundamental statistics across different simulation runs. This generates a rich, synthetic dataset of simulated points, where each point has associated input statistics and a binary win/loss outcome. Second, this simulated dataset becomes the input for a feature importance analysis using logistic regression or SHAP values. This allows the application to *learn* the complex relationships between the input fundamental statistics and the point outcome *as generated by its own internal simulation logic*. This approach is significantly more powerful than a simple "what-if" sensitivity analysis on a single baseline, as it accounts for the full range of probabilistic interactions and dependencies modeled within the simulation, providing a more accurate and comprehensive quantification of impact.4  
A crucial aspect of beach volleyball performance, beyond direct point-scoring actions, involves "controlled" or "enabling" actions. Metrics such as "Positive Block Touches" 10 and "Controlled Blocks" 14 are identified as important, even though they do not directly score a point. As highlighted, a middle blocker with many positive touches but fewer stuff blocks might be more valuable than one with more stuff blocks but fewer overall touches.10 These actions, while not immediately terminal, significantly influence the  
*subsequent* rally dynamics. For example, a positive block touch can slow down an attack or redirect it into a more defensible area, thereby increasing the probability of a successful dig by the defending teammate.10 This, in turn, increases the chance of the team successfully transitioning to offense and ultimately winning the rally through a counter-attack. Therefore, the importance analysis will not be limited to quantifying the impact of statistics that directly score points (e.g., Serve Ace %, Attack Kill %). It will also quantify the importance of these "controlled" or "enabling" statistics. This is achieved by allowing the simulation to model the full rally flow (as per the Markov chain design) and then observing how changes in these non-terminal statistics (e.g., increasing  
Positive Block Touch %) lead to changes in the *overall point win probability* over many simulated rallies. This provides a more holistic and accurate view of what truly contributes to winning a point in beach volleyball, recognizing the value of actions that enable subsequent successful plays rather than just direct scoring.

### **Output Metrics for Importance Analysis**

The application will provide clear and actionable output from the importance analysis:

* **Quantified Marginal Impact**: For each fundamental statistic, the application will provide a clear statement of its impact on point win probability. This can be expressed as: "An X% absolute increase in leads to a Y% absolute increase/decrease in point win probability." This directly fulfills the user query. Alternatively, it can be stated as: "A 1-unit increase in increases the odds of winning a point by a factor of Z," derived from logistic regression odds ratios.22  
* **Ranked List of Importance**: A ranked list of fundamental statistics, ordered from most to least important for winning a point, will be presented based on the calculated impacts.  
* **Visualization**: Graphical representations of the sensitivity results, such as bar charts showing the magnitude of impact or spider charts comparing impacts across different statistics, will be provided for intuitive understanding.

### **Table 3: Example Sensitivity Analysis Results**

The following table provides an example of how the sensitivity analysis results will be presented, illustrating the quantifiable impact of changes in fundamental statistics on point win probability. This format offers actionable insights for strategic decision-making and training prioritization.

| Fundamental Statistic | Change in Statistic | Baseline Win Probability (Team A) | New Win Probability (Simulated) | Absolute Change in Win Probability | Relative Change in Win Probability | Interpretation |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Reception Quality (Perfect Pass) % | \+5% (absolute) | 50.0% | 52.5% | \+2.5 percentage points | \+5.0% | A 5% absolute increase in Perfect Reception % leads to a 2.5 percentage point increase in point win probability, representing a 5.0% relative improvement. |
| Hitting Efficiency % | \+0.03 (e.g., from.300 to.330) | 50.0% | 51.8% | \+1.8 percentage points | \+3.6% | Increasing Hitting Efficiency by 0.03 (e.g., 3 percentage points) leads to a 1.8 percentage point increase in point win probability. |
| Serve Ace % | \+2% (absolute) | 50.0% | 50.7% | \+0.7 percentage points | \+1.4% | A 2% absolute increase in Serve Ace % leads to a 0.7 percentage point increase in point win probability. |
| Positive Block Touch % | \+5% (absolute) | 50.0% | 51.2% | \+1.2 percentage points | \+2.4% | A 5% absolute increase in Positive Block Touch % leads to a 1.2 percentage point increase in point win probability, enhancing defensive transition. |
| Dig % | \+3% (absolute) | 50.0% | 50.9% | \+0.9 percentage points | \+1.8% | A 3% absolute increase in Dig % leads to a 0.9 percentage point increase in point win probability, improving rally continuation. |

## **VI. Technical Architecture Considerations**

The successful development and deployment of this application will rely on a robust and scalable technical architecture.

### **Modular Architecture**

The application should be designed with a modular architecture to ensure scalability, maintainability, and extensibility. This approach facilitates independent development, testing, and deployment of components.

* **Data Input Module**: This module will manage the ingestion of team fundamental statistics. Its interface could range from a user-friendly web form to an API endpoint for programmatic input (e.g., JSON, CSV upload), or a file-based input system. Robust validation rules will be implemented to ensure the quality of input data and adherence to defined ranges and formats.  
* **Simulation Engine**: This is the core computational component, responsible for executing the Monte Carlo simulations of beach volleyball points. It will implement the Markov chain logic for rally progression and probabilistic outcomes. For efficient handling of large numbers of simulations, this module should be implemented in a high-performance language such as Python (leveraging libraries like NumPy/SciPy), Java, or C++. Its design should inherently support scalability, potentially leveraging multi-threading or parallel processing for faster execution of extensive simulation batches.  
* **Analytics Module**: This module will perform the statistical importance analysis, including logistic regression and SHAP value calculations, on the simulated point data. It will utilize established statistical libraries (e.g., scikit-learn in Python, R packages) to ensure accuracy and efficiency in its computations.  
* **Data Storage Layer**: This layer will be responsible for persistently storing input team statistics, raw point-by-point simulation results (essential for detailed analysis), and aggregated analysis outcomes. A relational database (e.g., PostgreSQL, MySQL) would be suitable for structured data, while a NoSQL database (e.g., MongoDB) might be considered if greater flexibility for granular rally data is prioritized.  
* **User Interface (UI) / Reporting Module**: This module will provide an intuitive interface for users to input data, trigger simulations, and visualize the results. It will present simulation summaries, point win probabilities, and the statistical importance analysis through clear tables and charts. A web-based framework (e.g., React, Angular, Vue.js) would ensure broad accessibility and interactivity.32  
* **API Layer (Optional but Recommended)**: Implementing a RESTful API layer will expose the core simulation and analysis functionalities, enabling seamless integration with other systems or custom front-end applications.

### **Performance and Scalability Considerations**

The nature of Monte Carlo simulations, which require running thousands to millions of points to achieve statistical significance 4, imposes significant performance and scalability requirements on the application. The architecture must be capable of supporting this substantial computational load.  
The inherent requirement for a high volume of simulations directly translates into significant computational demands for the application. The "Simulation Engine" must be designed for high performance, implying the need for efficient algorithms, potentially parallel processing capabilities (e.g., multi-threading or distributed computing), and optimization of data structures to minimize overhead. The "Analytics Module" will also need to be capable of processing and analyzing these large datasets generated by the simulation efficiently. This highlights that the choice of programming language, core libraries, and underlying infrastructure (e.g., whether to deploy on a single server or leverage cloud-based scalable compute resources) is not trivial. These decisions will directly impact the application's ability to deliver results within a reasonable timeframe, which is crucial for user experience and practical utility.  
Furthermore, generating detailed point-by-point data for analysis will result in substantial data volumes. The data storage and analytics modules must be optimized to handle and process this volume efficiently. For interactive use, the simulation and analysis processes should complete within an acceptable timeframe, which might necessitate asynchronous processing or cloud-based scaling solutions.  
The detailed discussion regarding the incorporation of nuanced metrics (e.g., Pass Quality Rating, Positive Block Touches) and the modeling of rally progression using Markov chain states that include "efficacy" (quality of execution) implies that the simulation will generate highly granular data for each rally. This is not merely a binary win/loss outcome per point, but a sequence of states and their qualities (e.g., Serve\_Outcome, Reception\_Quality, Set\_Quality, Attack\_Outcome, Defensive\_Action\_Type). The "Data Storage Layer" and the "Analytics Module" must be specifically designed to capture, store, and process this rich, detailed, point-by-point data. This means choosing a database schema that can accommodate sequences of events and their associated attributes, rather than just aggregate statistics. This granular data is absolutely crucial for the "Statistical Importance Analysis" phase, especially if employing advanced methods like logistic regression or SHAP values, as these methods thrive on detailed feature information to uncover subtle relationships. This design choice, while adding initial complexity, significantly enhances the application's future versatility, enabling more sophisticated analyses that go beyond the initial query.

## **VII. Future Enhancements and Considerations**

Building upon the core functionalities, several enhancements can be considered for future versions of the application to increase its realism, utility, and analytical depth.

* **Player-Specific Statistics and Lineup Optimization**: An enhancement could allow the input of individual player statistics (e.g., Player A's serve efficiency, Player B's reception quality) rather than solely aggregated team statistics. This would enable the simulation to model specific player matchups and facilitate "what-if" scenarios regarding lineup changes or player substitutions (e.g., evaluating the impact of Player A serving instead of Player B). Such a capability would be invaluable for optimizing team composition and roles, as beach volleyball teams often specialize players in blocking and defense.2  
* **Fatigue and Momentum Dynamics**: Incorporating more sophisticated models for player fatigue would allow for the degradation of performance statistics over the course of a match or tournament. This would add another layer of realism, enabling the simulation to predict how performance might decline in longer matches or multi-day tournaments. While existing research discusses using pre-season data to predict season performance 33, an in-game fatigue model would be a natural extension for dynamic simulations. Additionally, further development of the "momentum" model could include more nuanced psychological factors or even opponent reactions to momentum shifts.  
* **Opponent Tendencies and Strategic Adjustments**: Allowing users to input opponent-specific tendencies (e.g., preferred attack zones, serve targets in pressure situations, defensive adjustments after timeouts) would significantly enhance the simulation's strategic depth. The application could then model strategic interactions more accurately, enabling users to test different game plans against specific opponents.10 This moves beyond purely statistical averages to incorporate tactical intelligence.  
* **Environmental Factors Integration**: While current beach volleyball rules account for wind and sun by mandating side switching 2, a more advanced model could incorporate dynamic environmental factors, such as real-time wind speed and direction, and their probabilistic impact on serve, attack, and reception outcomes.  
* **Real-time Data Integration and In-Game Predictions**: Integrating the simulation engine with real-time match data feeds would transform the application into a live analytics tool. This would enable it to provide real-time in-game win probability predictions and suggest tactical adjustments based on live performance.4  
* **Advanced Machine Learning for Probability Derivation**: Instead of relying solely on manually defined conditional probabilities, future versions could leverage historical match data and advanced machine learning models (e.g., deep learning, Bayesian networks) to *learn* the complex, non-linear relationships and conditional probabilities between different rally actions and their outcomes. This would make the model more data-driven, adaptive, and potentially more accurate, especially as more granular real-world data becomes available.20  
* **Interactive User Interface for Scenario Testing**: Developing a highly interactive UI that allows users to intuitively adjust individual input parameters (e.g., sliders for "Perfect Pass %," "Hitting Efficiency") and immediately visualize the impact on simulated win probability and other key outcomes would greatly enhance the user experience for "what-if" analysis. This would make the application an even more powerful tool for strategic exploration and performance improvement.

## **VIII. Conclusions and Recommendations**

The proposed application specification outlines a powerful tool for analyzing beach volleyball performance. By meticulously modeling the sport's mechanics through a Markov chain approach and employing Monte Carlo simulations, the application can accurately predict point outcomes based on team fundamental statistics. The integration of nuanced metrics and dynamic elements like short-term momentum ensures a high degree of realism in the simulations.  
A key strength of this application lies in its ability to go beyond simple simulation. By applying advanced statistical techniques such as logistic regression and SHAP values to the rich, simulated data, it can precisely quantify the impact of each fundamental skill on the probability of winning a point. This capability directly addresses the user's need to understand which statistics are most important for success, providing actionable insights in a clear, interpretable format.  
The modular technical architecture proposed will ensure the application's scalability and maintainability, crucial for handling computationally intensive simulations and large datasets. The emphasis on data granularity will also lay the groundwork for future, more sophisticated analyses. Ultimately, this application will serve as an indispensable resource for beach volleyball teams and analysts, enabling data-driven decision-making to optimize training, refine strategies, and gain a significant competitive advantage.

#### **Works cited**

1. OFFICIAL BEACH VOLLEYBALL RULES 2021-2024 \- FIVB, accessed July 10, 2025, [https://www.fivb.com/wp-content/uploads/2024/03/FIVB-Beach\_Volleyball\_Rules\_2021\_2024-EN.pdf](https://www.fivb.com/wp-content/uploads/2024/03/FIVB-Beach_Volleyball_Rules_2021_2024-EN.pdf)  
2. Rules of Volleyball \- USA Volleyball, accessed July 10, 2025, [https://usavolleyball.org/play/rules-of-volleyball/](https://usavolleyball.org/play/rules-of-volleyball/)  
3. The Mathematics of Volleyball \- Ken Shirriff's blog, accessed July 10, 2025, [http://www.righto.com/2011/07/mathematics-of-volleyball.html](http://www.righto.com/2011/07/mathematics-of-volleyball.html)  
4. Full article: Play-by-Play Volleyball Win Probability Model \- Taylor and Francis, accessed July 10, 2025, [https://www.tandfonline.com/doi/full/10.1080/00031305.2025.2490786?src=exp-la](https://www.tandfonline.com/doi/full/10.1080/00031305.2025.2490786?src=exp-la)  
5. Bayesian hierarchical models for the prediction of volleyball results \- PMC, accessed July 10, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9042147/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9042147/)  
6. On the winning probabilities and mean durations of volleyball \- ResearchGate, accessed July 10, 2025, [https://www.researchgate.net/publication/270258388\_On\_the\_winning\_probabilities\_and\_mean\_durations\_of\_volleyball](https://www.researchgate.net/publication/270258388_On_the_winning_probabilities_and_mean_durations_of_volleyball)  
7. How to Play Volleyball – Rules & Key Moves | Olympic Channel, accessed July 10, 2025, [https://www.olympics.com/en/news/how-to-play-volleyball](https://www.olympics.com/en/news/how-to-play-volleyball)  
8. 2v2 SAND VOLLEYBALL RULES GENERAL INFORMATION Rule 1\. Court and Equipment Section 1\. Location ART. 2 … All matches will be p \- FIU Division of Student Affairs, accessed July 10, 2025, [https://dasa.fiu.edu/all-departments/wellness-recreation-centers/\_assets/2v2-sand-volleyball-rules-summer-a-2024.pdf](https://dasa.fiu.edu/all-departments/wellness-recreation-centers/_assets/2v2-sand-volleyball-rules-summer-a-2024.pdf)  
9. Basic Rules – FIVB, accessed July 10, 2025, [https://www.fivb.com/beach-volleyball/the-game/basic-rules/](https://www.fivb.com/beach-volleyball/the-game/basic-rules/)  
10. Advanced Volleyball Metrics That Drive D3 Success – InsideHitter.com, accessed July 10, 2025, [https://insidehitter.com/2025/03/09/advanced-volleyball-metrics-that-drive-d3-success/](https://insidehitter.com/2025/03/09/advanced-volleyball-metrics-that-drive-d3-success/)  
11. Volleyball Stat Definitions \- Amazon S3, accessed July 10, 2025, [https://s3.amazonaws.com/my.llfiles.com/00058620/VolleyballStatDefinitions.pdf](https://s3.amazonaws.com/my.llfiles.com/00058620/VolleyballStatDefinitions.pdf)  
12. Volleyball Statistics\_20160512 \- AWS, accessed July 10, 2025, [https://siplay-static.s3.amazonaws.com/forms/Stat%20Listings/VolleyballStatistics.pdf](https://siplay-static.s3.amazonaws.com/forms/Stat%20Listings/VolleyballStatistics.pdf)  
13. Characteristics of Serve, Reception and Set That ... \- Frontiers, accessed July 10, 2025, [https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.00222/full](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.00222/full)  
14. Statistics \- AVP Beach Volleyball, accessed July 10, 2025, [https://avp.com/statistics/](https://avp.com/statistics/)  
15. Reception-attack relation in men's and women's volleyball during ..., accessed July 10, 2025, [https://efsupit.ro/images/stories/iulie2020/Art%20271.pdf](https://efsupit.ro/images/stories/iulie2020/Art%20271.pdf)  
16. The Sequencing of Game Complexes in Women's Volleyball, accessed July 10, 2025, [https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.00739/full](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.00739/full)  
17. Markovian sports: Tennis vs. Volleyball \- UB, accessed July 10, 2025, [https://www.ub.edu/probabilitats-seminaribcn/Curs2012/ferrante.pdf](https://www.ub.edu/probabilitats-seminaribcn/Curs2012/ferrante.pdf)  
18. Week 2 – Overview of Stochastic Processes, accessed July 10, 2025, [https://web.stanford.edu/class/stats50/files/STATS\_50\_Markov\_Chains.pdf](https://web.stanford.edu/class/stats50/files/STATS_50_Markov_Chains.pdf)  
19. How does the SportsLine simulation model make picks?, accessed July 10, 2025, [https://help.sportsline.com/s/article/How-does-the-SportsLine-simulation-model-make-picks](https://help.sportsline.com/s/article/How-does-the-SportsLine-simulation-model-make-picks)  
20. Modeling In-Match Sports Dynamics Using the Evolving Probability ..., accessed July 10, 2025, [https://www.mdpi.com/2076-3417/11/10/4429](https://www.mdpi.com/2076-3417/11/10/4429)  
21. Teaching Game and Simulation Based Probability \- ERIC, accessed July 10, 2025, [https://files.eric.ed.gov/fulltext/EJ1246386.pdf](https://files.eric.ed.gov/fulltext/EJ1246386.pdf)  
22. 7 Key Stats: Logistic Regression in Sports Analytics, accessed July 10, 2025, [https://www.numberanalytics.com/blog/7-key-stats-logistic-regression-sports-analytics](https://www.numberanalytics.com/blog/7-key-stats-logistic-regression-sports-analytics)  
23. 10 Proven Ways to Use Logistic Regression in Sports Data \- Number Analytics, accessed July 10, 2025, [https://www.numberanalytics.com/blog/10-proven-ways-logistic-regression-sports-data](https://www.numberanalytics.com/blog/10-proven-ways-logistic-regression-sports-data)  
24. Binary logistic regression in R \- Stats and R, accessed July 10, 2025, [https://statsandr.com/blog/binary-logistic-regression-in-r/](https://statsandr.com/blog/binary-logistic-regression-in-r/)  
25. Full article: A review of the transition from Shapley values and SHAP values to RGE, accessed July 10, 2025, [https://www.tandfonline.com/doi/full/10.1080/02331888.2025.2487853?af=R](https://www.tandfonline.com/doi/full/10.1080/02331888.2025.2487853?af=R)  
26. Shapley and Owen values for model output explainability: a hands-on case study, accessed July 10, 2025, [https://www.bbvaaifactory.com/shapley-and-owen-values-for-model-output-explainability-a-hands-on-case-study/](https://www.bbvaaifactory.com/shapley-and-owen-values-for-model-output-explainability-a-hands-on-case-study/)  
27. Feature importance based on SHAP-values. On the left side, the mean... \- ResearchGate, accessed July 10, 2025, [https://www.researchgate.net/figure/Feature-importance-based-on-SHAP-values-On-the-left-side-the-mean-absolute-SHAP-values\_fig3\_349883007](https://www.researchgate.net/figure/Feature-importance-based-on-SHAP-values-On-the-left-side-the-mean-absolute-SHAP-values_fig3_349883007)  
28. 4.7. SHAP (SHapley Additive exPlanations) \- PiML Toolbox, accessed July 10, 2025, [https://selfexplainml.github.io/PiML-Toolbox/\_build/html/guides/explain/shap.html](https://selfexplainml.github.io/PiML-Toolbox/_build/html/guides/explain/shap.html)  
29. How to Perform a Sensitivity Analysis in COMSOL Multiphysics, accessed July 10, 2025, [https://www.comsol.com/blogs/how-to-perform-a-sensitivity-analysis-in-comsol-multiphysics](https://www.comsol.com/blogs/how-to-perform-a-sensitivity-analysis-in-comsol-multiphysics)  
30. Parameter Sensitivity Analysis of Stochastic Models Provides Insights into Cardiac Calcium Sparks \- PMC, accessed July 10, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC3870797/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3870797/)  
31. What Is Sensitivity Analysis? \- Investopedia, accessed July 10, 2025, [https://www.investopedia.com/terms/s/sensitivityanalysis.asp](https://www.investopedia.com/terms/s/sensitivityanalysis.asp)  
32. Balltime \- AI Platform for Volleyball Highlights & Analytics, accessed July 10, 2025, [https://www.balltime.com/](https://www.balltime.com/)  
33. (PDF) Predicting Volleyball Season Performance Using Pre-Season Wearable Data and Machine Learning \- ResearchGate, accessed July 10, 2025, [https://www.researchgate.net/publication/389748307\_Predicting\_Volleyball\_Season\_Performance\_Using\_Pre-Season\_Wearable\_Data\_and\_Machine\_Learning](https://www.researchgate.net/publication/389748307_Predicting_Volleyball_Season_Performance_Using_Pre-Season_Wearable_Data_and_Machine_Learning)  
34. Developing an Analytics Strategy in Volleyball | AVCA Blog, accessed July 10, 2025, [https://www.avca.org/blog/the-guide-to-developing-an-analytics-strategy/](https://www.avca.org/blog/the-guide-to-developing-an-analytics-strategy/)  
35. 8 Ways Predictive Analysis Elevates Sports Strategy and Results \- Number Analytics, accessed July 10, 2025, [https://www.numberanalytics.com/blog/predictive-analysis-sports-strategy](https://www.numberanalytics.com/blog/predictive-analysis-sports-strategy)  
36. Sports Analytics: What is it & How it Improves Performance? \- Catapult, accessed July 10, 2025, [https://www.catapult.com/blog/what-is-sports-analytics](https://www.catapult.com/blog/what-is-sports-analytics)