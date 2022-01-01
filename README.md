<h1 align="center">Tonminer</h1>
<h3 align="center">Tonminer-cuda for ton-proxy (solomining)</h3>
<p align="center">Optimized from the <a href="https://github.com/tontechio/pow-miner-gpu">original client</a> ,
miner for <a href="https://github.com/GRinvest/ton-proxy">ton-proxy</a> </p>
<hr />
<p>The installation of the miner is quite simple, you will need:</p>
<ul>
 <li>Ubuntu system (from 18.04) with Nvidia video cards</li>
 <li>Installed on a separate server, with an external ip address <a href="https://github.com/GRinvest/ton-proxy">ton-proxy</a></li>
</ul>
<p> Login to your rig and enter commands in the terminal:</p>
<pre><code>
mkdir tonminer-cuda
cd tonminer-cuda
wget https://github.com/GRinvest/tonminer/releases/download/0.1.6/tonminer-cuda.tar.gz
tar xvf tonminer-cuda.tar.gz
rm tonminer-cuda.tar.gz
./tonminer-cuda -h
</code></pre>
<p>After starting <code>./tonminer-cuda -h</code>, you will be presented with a list of commands. Let's explore them in more detail:</p>

<table border="1">
   <caption>Command table</caption>
   <tr>
    <th>Command</th>
    <th>Description</th>
   </tr>
   <tr><td>-W</td><td>Required Parameter. Your Toncoin wallet address, not exchange (etc. EQA1VNu5w...)</td></tr>
   <tr><td>-H</td><td>Required Parameter. Host (IP address) where the ton-proxy is running (etc. 192.168.1.1)</td></tr>
   <tr><td>-P</td><td>Required Parameter. The port on which the proxy is running (default: 8080)</td></tr>
   <tr><td>-F</td><td>Optional Parameter. 1..65536, the multiplier for throughput, affects the number of hashes processed per iteration on the GPU (default: 64) So far, one for all video cards</td></tr>
   <tr><td>-B</td><td>Optional Parameter. Start benchmarking: Optimal Boost Factor (default: disabled) This parameter is described below.</td></tr>
   <tr><td>-C</td><td>Optional Parameter. path global.config.json (default: it is already in the program but you can specify your)</td></tr>
   <tr><td>-L</td><td>Optional Parameter. path lite-client (default: it is already in the program but you can specify your)</td></tr>
   <tr><td>-M</td><td>Optional Parameter. path miner-client (default: it is already in the program but you can specify your)</td></tr>
</table>
<p>In general, the launch command looks like this:</p>
<pre><code>./tonminer-cuda -H 192.168.1.1 -P 8080 -W EQA1VNu5wZAWdo4MmHX8i2LWZ7mFmyu6BCh0KbwmQitEB3xC</code></pre>
<hr />
<p>If you want to run the benchmark, add the parameter<code>-B</code></p>
<p>Example<code>./tonminer-cuda -H 192.168.1.1 -P 8080 -W EQA1VNu5wZAWdo4MmHX8i2LWZ7mFmyu6BCh0KbwmQitEB3xC -B</code></p>
<p>After that, run the benchmark, which will take about 30 minutes. at the end, a file will be created where you can see the results for each video card</p>
<pre><code>nano /var/log/gpu_benchmark.json</code></pre>
<p>Choose one optimal parameter for all maps and use it together with the command <code>-F</code></p>
<hr />
<p>If you liked my development and would like to support the project. I would be grateful for all possible help:</p>
<p>TON: <code>EQCtpc260pZIxRlifzmbefdHm4gUTKAMbmwaFebo7WiBiGc9</code></p>
<p>For questions and suggestions, please contact <a href="https://t.me/tonsolominingdev">Telegram Group</a></p>
<hr />
<p>Some functions for work Lite-client are taken from <a href="https://github.com/igroman787/mytonctrl">here</a>. Thank you very much to the author.</p>
<p>Also a huge gratitude, in helping to create the project <a href="https://github.com/wolfpro/">wolfpro</a></p>
<p>P.S. I see how the project is actively developing, so it is very interesting to start developing TON for the entire eco-system. I want to wish the developers success in this difficult matter and the entire community </p>
<p><q>Never doubt that a small group of thoughtful, citizens can change the world. Indeed, it is the only thing that ever has.</q> - Margaret Mead</p>
<hr />
<p align="center"><i>Tonminer-cuda is <a href="https://github.com/GRinvest/tonminer/blob/master/LICENSE.md">BSD licensed</a> code.<br/>Designed & built in Novosibirsk, Russia.</i></p>


