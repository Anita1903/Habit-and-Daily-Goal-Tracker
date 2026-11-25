const $=id=>document.getElementById(id);
$("today").textContent=new Date().toLocaleDateString(undefined,{weekday:"long",day:"numeric",month:"long",year:"numeric"});
async function api(url,opts={}){const r=await fetch(url,{headers:{"Content-Type":"application/json"},...opts});const d=await r.json();if(!r.ok)throw Error(d.error||"Something went wrong");return d}
function notify(msg){alert(msg)}
async function load(){try{const [habits,stats]=await Promise.all([api("/api/habits"),api("/api/stats")]);
$("total").textContent=stats.total_habits;$("completed").textContent=stats.completed_today;$("percent").textContent=stats.completion_percent+"%";$("progress").style.width=stats.completion_percent+"%";
$("habits").innerHTML=habits.map(h=>`<div class="habit"><div class="habit-left"><button class="check ${h.done_today?'done':''}" onclick="toggle(${h.id})">${h.done_today?'✓':''}</button><div><div class="habit-name ${h.done_today?'done':''}">${escapeHtml(h.name)}</div><div class="meta">${escapeHtml(h.category)} · 🔥 ${h.streak} day streak</div></div></div><div class="actions"><button class="edit" onclick="editHabit(${h.id},${JSON.stringify(h.name).replace(/</g,'\\u003c')},${JSON.stringify(h.category)})">Edit</button><button class="delete" onclick="removeHabit(${h.id})">Delete</button></div></div>`).join("");
$("empty").hidden=habits.length>0;
$("week").innerHTML=stats.weekly.map(d=>`<div class="day"><div class="bar-wrap"><div class="bar" style="height:${Math.min(100,d.count*22)}%"></div></div><b>${d.day}</b><small>${d.count}</small></div>`).join("");
}catch(e){notify(e.message)}}
function escapeHtml(s){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
$("habitForm").addEventListener("submit",async e=>{e.preventDefault();try{await api("/api/habits",{method:"POST",body:JSON.stringify({name:$("habitName").value,category:$("category").value})});$("habitName").value="";load()}catch(e){notify(e.message)}});
async function toggle(id){try{await api(`/api/habits/${id}/checkin`,{method:"POST",body:"{}"});load()}catch(e){notify(e.message)}}
async function removeHabit(id){if(!confirm("Delete this habit and its check-in history?"))return;try{await api(`/api/habits/${id}`,{method:"DELETE"});load()}catch(e){notify(e.message)}}
async function editHabit(id,name,category){const n=prompt("Update habit name:",name);if(n===null)return;const c=prompt("Category:",category);if(c===null)return;try{await api(`/api/habits/${id}`,{method:"PUT",body:JSON.stringify({name:n,category:c})});load()}catch(e){notify(e.message)}}
load();
