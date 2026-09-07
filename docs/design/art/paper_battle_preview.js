"use strict";
const stage=document.getElementById("stage");
const viewport=document.getElementById("viewport");
const get=id=>document.getElementById(id);
const cards=[
  {id:"transfer",name:"关键转账记录",type:"证据",phase:"法庭调查",effect:"获得 1 枚「伏笔」。\n已有伏笔时，改为\n法官心证 +6。",hint:"用前序证据铺垫后续论证",consume:"本场消耗",once:true},
  {id:"note",name:"借条原件",type:"证据",phase:"法庭调查",effect:"法官心证 +4。\n若已有「伏笔」，\n额外获得 2 点心证。",hint:"出示关键书面材料",consume:"本场消耗",once:true},
  {id:"question",name:"笔迹质证",type:"质证",phase:"法庭调查",effect:"法官心证 +3。\n对方下次质疑造成的\n心证损失减少 2 点。",hint:"准备回应对方的质疑",consume:"循环使用",once:false},
  {id:"procedure",name:"程序抗辩",type:"程序",phase:"全阶段",effect:"法官心证 +2。\n对方本回合造成的\n心证损失减少 2 点。",hint:"以程序规则回应质疑",consume:"循环使用",once:false},
  {id:"law",name:"法条援引",type:"法条",phase:"法庭辩论",effect:"法官心证 +5。\n当前为法庭调查阶段，\n这张牌暂不可使用。",hint:"阶段不符 · 锁定",consume:"循环使用",locked:true}
];
let selected=null,busy=false,conviction=50,clues=0,shield=0,round=1;
let used=new Set(),autoTimer=null,automatic=false,epoch=0;
const reduceMedia=window.matchMedia("(prefers-reduced-motion: reduce)");
let reduced=reduceMedia.matches,paused=false;
function resize(){const scale=viewport.clientWidth/1600;stage.style.transform=`scale(${scale})`;viewport.style.height=`${900*scale}px`;}
new ResizeObserver(resize).observe(viewport);resize();
function renderHand(){
  get("hand").innerHTML=cards.map((c,i)=>`<div class="card-slot${selected===c.id?" selected":""}" style="--arc:${[10,3,0,3,10][i]}px;--angle:${[-2,-1,0,1,2][i]}deg"><button class="card${used.has(c.id)?" used":""}" data-card="${c.id}" aria-pressed="${selected===c.id}" ${c.locked||used.has(c.id)?"disabled":""} aria-label="${c.name}，${c.type}，${c.locked?"阶段不符":c.consume}"><span class="card-title">${c.name}</span><span class="card-type">${c.type} · ${c.phase}</span><span class="art-overlay" aria-hidden="true"><i class="art-thread"></i><i class="art-dot"></i></span><span class="card-rules"><strong>${used.has(c.id)?"已使用":c.locked?"阶段不符":"效果"}</strong><p>${c.effect}</p><small>${c.hint}</small></span><span class="card-footer">${used.has(c.id)?c.once?"已移出本场":"下回合恢复":c.consume}</span></button></div>`).join("");
  get("hand").querySelectorAll("[data-card]").forEach(button=>button.addEventListener("click",()=>selectCard(button.dataset.card)));
}
function status(text){get("status").textContent=text;}
function selectCard(id){if(busy)return;const card=cards.find(c=>c.id===id);if(!card||card.locked||used.has(id))return;selected=id;renderHand();get("play").disabled=false;get("play").textContent=`出示「${card.name}」`;status(`${card.name}已选中。确认后生效；Esc 可取消。`);}
function cancelSelection(){if(busy)return;selected=null;renderHand();get("play").disabled=true;get("play").textContent="选中后出牌";status("已取消。选择其他材料继续举证。");}
function updateHud(){get("conviction-number").textContent=conviction;get("conviction-fill").style.width=`${conviction}%`;stage.querySelector(".meter").setAttribute("aria-valuenow",conviction);get("clue-label").textContent=`伏笔 ${clues}`;get("round-label").textContent=`第 ${round} 回合`;}
const rest=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function animateActor(id,kind="argue"){
  if(reduced||paused)return;
  const toward=id==="opponent"?-1:1;
  const frames=kind==="nod"?[{transform:"rotate(0deg)"},{transform:"rotate(1.4deg) translateY(3px)"},{transform:"rotate(0deg)"}]:[{transform:"translateX(0)"},{transform:`translateX(${12*toward}px) rotate(${1.6*toward}deg)`},{transform:"translateX(0)"}];
  await get(id).animate(frames,{duration:kind==="nod"?540:680,easing:"ease-in-out"}).finished.catch(()=>{});
}
async function impact(text){get("impact-text").textContent=text;if(reduced||paused)return;await get("impact").animate([{opacity:0,transform:"scale(.82)"},{opacity:1,transform:"scale(1)",offset:.25},{opacity:0,transform:"scale(1.06)"}],{duration:850,easing:"ease-out"}).finished.catch(()=>{});}
async function flyCard(id){
  if(reduced||paused){await rest(60);return;}
  const source=stage.querySelector(`[data-card="${id}"]`);if(!source)return;
  const bounds=source.getBoundingClientRect(),box=stage.getBoundingClientRect(),scale=box.width/1600;
  const startX=(bounds.left-box.left)/scale,startY=(bounds.top-box.top)/scale;
  const ghost=document.createElement("div");ghost.className="flying-card";ghost.setAttribute("aria-hidden","true");ghost.style.left=`${startX}px`;ghost.style.top=`${startY}px`;ghost.append(source.cloneNode(true));stage.append(ghost);
  const endX=800-105-startX,endY=395-155-startY;
  const motion=ghost.animate([{transform:"translate(0,0) scale(1)",opacity:1},{transform:`translate(${endX*.6}px,${endY-40}px) rotate(-6deg) scale(.72)`,opacity:1,offset:.65},{transform:`translate(${endX}px,${endY}px) rotate(0) scale(.27)`,opacity:0}],{duration:720,easing:"cubic-bezier(.2,.7,.3,1)"});
  await motion.finished.catch(()=>{});ghost.remove();
}
async function playCard(){
  if(busy||!selected)return;const card=cards.find(c=>c.id===selected);if(!card||card.locked||used.has(card.id))return;
  const turnEpoch=epoch;busy=true;get("play").disabled=true;get("end-turn").disabled=true;status(`正在出示「${card.name}」……`);
  await Promise.all([flyCard(card.id),animateActor("player")]);if(turnEpoch!==epoch)return;
  let delta=0;if(card.id==="transfer"){if(clues>0)delta=6;else clues++;}else if(card.id==="note")delta=clues>0?6:4;else if(card.id==="question"){delta=3;shield+=2;}else if(card.id==="procedure"){delta=2;shield+=2;}
  conviction=Math.min(100,conviction+delta);used.add(card.id);selected=null;updateHud();renderHand();
  await Promise.all([impact(delta?`心证 +${delta}`:"伏笔已建立"),animateActor("judge","nod")]);if(turnEpoch!==epoch)return;
  busy=false;get("end-turn").disabled=false;get("play").textContent="选中后出牌";status(`「${card.name}」已生效。${delta?`心证 +${delta}。`:"获得 1 枚伏笔。"}${card.once?"本场移除。":"下回合恢复。"}`);
}
async function endTurn(){
  if(busy)return;busy=true;selected=null;get("play").disabled=true;get("end-turn").disabled=true;renderHand();const turnEpoch=epoch;
  status("对方正在质疑证据……");get("intent").textContent="正在质疑证据";
  await animateActor("opponent");if(turnEpoch!==epoch)return;
  const loss=Math.max(0,3-shield);conviction=Math.max(0,conviction-loss);shield=0;round++;cards.filter(c=>!c.once).forEach(c=>used.delete(c.id));updateHud();renderHand();
  await impact(loss?`心证 −${loss}`:"程序回应生效");if(turnEpoch!==epoch)return;
  status(`对方质疑：心证 −${loss}。进入第 ${round} 回合，循环卡已恢复。`);get("intent").textContent="下一步：质疑证据";busy=false;get("end-turn").disabled=false;get("play").textContent="选中后出牌";
}
function stopAuto(){automatic=false;clearTimeout(autoTimer);get("auto").setAttribute("aria-pressed","false");get("auto").textContent="自动演示";}
function autoStep(){if(!automatic)return;if(!busy){const available=cards.find(c=>!c.locked&&!used.has(c.id));if(available){if(selected===available.id)playCard();else selectCard(available.id);}else endTurn();}autoTimer=setTimeout(autoStep,1800);}
get("auto").onclick=()=>{if(automatic)stopAuto();else{automatic=true;get("auto").setAttribute("aria-pressed","true");get("auto").textContent="停止演示";autoStep();}};
function syncMotion(){stage.classList.toggle("reduced",reduced);stage.classList.toggle("paused",paused);get("reduce").setAttribute("aria-pressed",String(reduced));get("pause").setAttribute("aria-pressed",String(paused));get("pause").textContent=paused?"恢复律动":"暂停律动";if(reduced||paused)stage.getAnimations({subtree:true}).filter(a=>!(a instanceof CSSAnimation)).forEach(a=>a.finish());}
get("pause").onclick=()=>{paused=!paused;syncMotion();};get("reduce").onclick=()=>{reduced=!reduced;syncMotion();};reduceMedia.addEventListener("change",e=>{reduced=e.matches;syncMotion();});
get("reset").onclick=()=>{epoch++;stopAuto();stage.getAnimations({subtree:true}).filter(a=>!(a instanceof CSSAnimation)).forEach(a=>a.cancel());stage.querySelectorAll(".flying-card").forEach(e=>e.remove());selected=null;busy=false;conviction=50;clues=0;shield=0;round=1;used.clear();updateHud();renderHand();get("play").disabled=true;get("end-turn").disabled=false;get("play").textContent="选中后出牌";get("intent").textContent="下一步：质疑证据";status("卷宗已展开。选择一张牌，开始举证。");};
get("play").onclick=playCard;get("end-turn").onclick=endTurn;document.addEventListener("keydown",e=>{if(e.key==="Escape")cancelSelection();});
for(let i=0;i<16;i++){const mote=document.createElement("i");mote.className="mote";mote.style.left=`${60+(i*139)%1480}px`;mote.style.top=`${290+(i*53)%310}px`;mote.style.setProperty("--time",`${11+i%6}s`);mote.style.setProperty("--delay",`${-i*.83}s`);stage.querySelector(".paper-wind").append(mote);}
syncMotion();renderHand();updateHud();
