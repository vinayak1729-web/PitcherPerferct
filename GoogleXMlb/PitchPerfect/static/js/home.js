 // Sidebar Toggle
 const toggleBtn = document.getElementById('toggle-btn');
 const sidebar = document.getElementById('sidebar');

 toggleBtn.addEventListener('click', () => {
     sidebar.classList.toggle('active');
     toggleBtn.textContent = sidebar.classList.contains('active') ? '<' : '>';
 });

 // Markdown Content
 const feedbackGemini = `{{ feedbackgemini }}`;

 // Render Markdown
 const md = window.markdownit();
 const markdownOutput = document.getElementById('markdown-output');
 markdownOutput.innerHTML = md.render(feedbackGemini);

 async function fetchData(team_id) {
     try {
         const response = await fetch(`/get_data?team_id=${team_id}`);
         if (!response.ok) {
             throw new Error('Network response was not ok');
         }
         const data = await response.json();
         console.log("Fetched Data:", data);  // Log the response data for debugging
         return data;
     } catch (error) {
         console.error('Error fetching data:', error);
         alert("Error fetching data, please try again later.");
     }
 }

 function generatePlotlyChart(fig, chartId) {
     Plotly.newPlot(chartId, fig.data, fig.layout);
 }

 function createGroupedBarChart(playersData, mlbAvg, chartId) {
     console.log("Players Data:", playersData);
     console.log("MLB Avg:", mlbAvg);

     // Ensure the data is available
     if (!playersData || playersData.length === 0 || !mlbAvg) {
         console.error("Missing data for the chart");
         return;
     }

     const playerNames = playersData.map(player => player['last_name, first_name']);
     const wobaData = playersData.map(player => parseFloat(player.woba) || 0);  // Handle non-numeric values gracefully
     const estWobaData = playersData.map(player => parseFloat(player.est_woba) || 0);  // Handle non-numeric values gracefully

     const mlbWoba = Array(playersData.length).fill(parseFloat(mlbAvg.woba) || 0);
     const mlbEstWoba = Array(playersData.length).fill(parseFloat(mlbAvg.est_woba) || 0);

     const traceWoba = {
         x: playerNames,
         y: wobaData,
         type: 'bar',
         name: 'Player wOBA',
         opacity: 0.6,
         barmode: 'group'
     };

     const traceEstWoba = {
         x: playerNames,
         y: estWobaData,
         type: 'bar',
         name: 'Player Estimated wOBA',
         opacity: 0.6,
         barmode: 'group'
     };

     const traceMlbWoba = {
         x: playerNames,
         y: mlbWoba,
         type: 'bar',
         name: 'MLB Avg wOBA',
         opacity: 0.6,
         marker: { color: 'red' },
         barmode: 'group'
     };

     const traceMlbEstWoba = {
         x: playerNames,
         y: mlbEstWoba,
         type: 'bar',
         name: 'MLB Avg Est wOBA',
         opacity: 0.6,
         marker: { color: 'blue' },
         barmode: 'group'
     };

     const layout = {
         title: `Grouped Bar Chart of Player wOBA vs Estimated wOBA vs MLB Avg`,
         barmode: 'group',
         xaxis: {
             title: 'Player',
             tickangle: -45,
             tickmode: 'array',
             tickvals: playerNames
         },
         yaxis: { title: 'wOBA / Est wOBA' },
         showlegend: true
     };

     const fig = {
         data: [traceWoba, traceEstWoba, traceMlbWoba, traceMlbEstWoba],
         layout: layout
     };

     generatePlotlyChart(fig, chartId);
 }

 const team_id = document.getElementById("team_id").querySelector("strong").textContent;
 console.log("Team ID:", team_id); // Log the team_id for debugging

 // Fetch data for Batters and Pitchers
 fetchData(team_id).then(data => {
     if (data) {
         // Batters data and MLB average for Batters
         if (data.batters && data.mlb_avg_batter) {
             const battersData = data.batters;
             const mlbAvgBatter = data.mlb_avg_batter;
             createGroupedBarChart(battersData, mlbAvgBatter, 'battersChart');
         } else {
             console.error("Batters data or MLB average for Batters is missing");
         }

         // Pitchers data and MLB average for Pitchers
         if (data.pitchers && data.mlb_avg_pitcher) {
             const pitchersData = data.pitchers;
             const mlbAvgPitcher = data.mlb_avg_pitcher;
             createGroupedBarChart(pitchersData, mlbAvgPitcher, 'pitchersChart');
         } else {
             console.error("Pitchers data or MLB average for Pitchers is missing");
         }
     } else {
         console.error("No data found");
     }
 });

 // JavaScript for Chatbot Functionality
document.getElementById("chatbot-trigger").addEventListener("click", () => {
 const chatbotContainer = document.getElementById("chatbot-container");
 chatbotContainer.style.display =
     chatbotContainer.style.display === "none" || chatbotContainer.style.display === ""
         ? "block"
         : "none";
});

document.getElementById("close-chatbot").addEventListener("click", () => {
 document.getElementById("chatbot-container").style.display = "none";
});

document.getElementById("send-message").addEventListener("click", async () => {
 const inputField = document.getElementById("chatbot-input");
 const userMessage = inputField.value.trim();

 if (!userMessage) return;

 // Append User Message
 const messagesContainer = document.getElementById("chatbot-messages");
 const userMessageElement = document.createElement("div");
 userMessageElement.innerText = `You: ${userMessage}`;
 userMessageElement.style.color = "blue";
 messagesContainer.appendChild(userMessageElement);

 // Scroll to the bottom
 messagesContainer.scrollTop = messagesContainer.scrollHeight;

 // Clear input field
 inputField.value = "";

 // Send the message to the backend and get a response
 const response = await fetch("/chatbot", {
     method: "POST",
     headers: {
         "Content-Type": "application/json",
     },
     body: JSON.stringify({ message: userMessage }),
 });

 const data = await response.json();

 // Append Bot Response
 const botMessageElement = document.createElement("div");
 botMessageElement.innerText = `PitcherPerfect: ${data.response}`;
 botMessageElement.style.color = "red";
 messagesContainer.appendChild(botMessageElement);

 // Scroll to the bottom
 messagesContainer.scrollTop = messagesContainer.scrollHeight;
});