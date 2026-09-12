/* Renderer and asset registration are shared by the preview and video export. */
const canvas = document.getElementById('room');
const ctx = canvas.getContext('2d');
const status = document.getElementById('status');
const panel = document.getElementById('panel');
const image = src => new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=reject;i.src=src});
const W=1672,H=941;
const entrance={x:1318,y:645}, desk={x:795,y:795};
const route=[entrance,{x:1180,y:729},{x:990,y:781},desk];
let background, sprites=[], atlas, player={...entrance}, current=null, facingLeft=true;
let exportMode=new URLSearchParams(location.search).has('export');

function extractFrames(source){
  const frames=[];
  for(let n=0;n<8;n++){
    const x=Math.round((n%4)*source.width/4), y=Math.round(Math.floor(n/4)*source.height/2);
    const width=Math.round((n%4+1)*source.width/4)-x, height=Math.round((Math.floor(n/4)+1)*source.height/2)-y;
    const work=document.createElement('canvas');work.width=width;work.height=height;
    const c=work.getContext('2d',{willReadFrequently:true});c.drawImage(source,x,y,width,height,0,0,width,height);
    const pixels=c.getImageData(0,0,width,height), d=pixels.data, count=width*height;
    // The generator supplied RGB checkerboard instead of alpha. Flood from
    // cell borders to remove only the connected neutral backing at render time.
    const removed=new Uint8Array(count), queue=new Int32Array(count);let head=0,tail=0;
    function offer(p){if(p<0||p>=count||removed[p])return;const i=p*4,r=d[i],g=d[i+1],b=d[i+2];if(Math.max(r,g,b)-Math.min(r,g,b)>19||Math.min(r,g,b)<112)return;removed[p]=1;queue[tail++]=p}
    for(let col=0;col<width;col++){offer(col);offer((height-1)*width+col)}
    for(let row=0;row<height;row++){offer(row*width);offer(row*width+width-1)}
    while(head<tail){const p=queue[head++];if(p%width)offer(p-1);if(p%width<width-1)offer(p+1);offer(p-width);offer(p+width)}
    for(let p=0;p<count;p++)if(removed[p])d[p*4+3]=0;
    // Keep the character's connected silhouette, dropping isolated paper marks.
    const seen=new Uint8Array(count);let largest=[];
    for(let p=0;p<count;p++){
      if(seen[p]||!d[p*4+3])continue;head=0;tail=0;queue[tail++]=p;seen[p]=1;
      while(head<tail){const a=queue[head++];for(const b of [a%width?a-1:-1,a%width<width-1?a+1:-1,a-width,a+width])if(b>=0&&b<count&&!seen[b]&&d[b*4+3]){seen[b]=1;queue[tail++]=b}}
      if(tail>largest.length)largest=Array.from(queue.subarray(0,tail));
    }
    const keep=new Uint8Array(count);for(const p of largest)keep[p]=1;
    let left=width,right=0,top=height,bottom=0;
    for(let p=0;p<count;p++){if(!keep[p]){d[p*4+3]=0;continue}left=Math.min(left,p%width);right=Math.max(right,p%width);top=Math.min(top,Math.floor(p/width));bottom=Math.max(bottom,Math.floor(p/width))}
    c.putImageData(pixels,0,0);
    let waistSum=0,waistCount=0;
    for(let yy=Math.round(top+(bottom-top)*.40);yy<top+(bottom-top)*.5;yy++)for(let xx=left;xx<=right;xx++)if(keep[yy*width+xx]){waistSum+=xx;waistCount++}
    const anchorX=waistSum/waistCount;
    const normalized=document.createElement('canvas');normalized.width=320;normalized.height=480;
    const draw=normalized.getContext('2d'),scale=436/(bottom-top+1);
    draw.drawImage(work,160-anchorX*scale,460-bottom*scale,width*scale,height*scale);
    frames.push(normalized);
  }
  atlas=document.createElement('canvas');atlas.width=1280;atlas.height=960;
  const a=atlas.getContext('2d');frames.forEach((f,n)=>a.drawImage(f,(n%4)*320,Math.floor(n/4)*480));
  return frames;
}

function pointAlong(points,t){
  const lengths=points.slice(1).map((p,i)=>Math.hypot(p.x-points[i].x,p.y-points[i].y));
  let remaining=Math.max(0,Math.min(1,t))*lengths.reduce((a,b)=>a+b,0);
  for(let i=0;i<lengths.length;i++){if(lengths[i]===0)continue;if(remaining<=lengths[i]||i===lengths.length-1){const q=remaining/lengths[i];return{x:points[i].x+(points[i+1].x-points[i].x)*q,y:points[i].y+(points[i+1].y-points[i].y)*q}}remaining-=lengths[i]}
  return {...points[points.length-1]};
}
function draw(position,frame=2,facingLeft=true){
  ctx.clearRect(0,0,W,H);ctx.drawImage(background,0,0,W,H);
  const bodyHeight=385+(position.y-645)*.31, scale=bodyHeight/436;
  ctx.save();ctx.translate(position.x,position.y);ctx.fillStyle='#241b1840';ctx.filter='blur(5px)';ctx.beginPath();ctx.ellipse(0,-3,56*scale,12*scale,0,0,Math.PI*2);ctx.fill();ctx.filter='none';
  ctx.scale(facingLeft?scale:-scale,scale);ctx.drawImage(sprites[frame],-160,-460);ctx.restore();
}
function demoAt(seconds){
  const progress=Math.max(0,Math.min(1,(seconds-.65)/6.4));
  const moving=seconds>=.65&&seconds<7.05;
  draw(pointAlong(route,progress),moving?Math.floor((seconds-.65)*8)%8:2);
  return {progress,frame:moving?Math.floor((seconds-.65)*8)%8:2};
}
function move(destination,open){
  panel.hidden=true;
  const target=destination==='desk'?desk:entrance;
  if(Math.hypot(player.x-target.x,player.y-target.y)<1){current=null;if(open)showPanel(open);return}
  const points=destination==='desk'?[player,{x:Math.max(player.x,990),y:781},desk]:[player,{x:990,y:781},{x:1180,y:729},entrance];
  current={points,start:performance.now(),duration:Math.max(900,points.slice(1).reduce((s,p,i)=>s+Math.hypot(p.x-points[i].x,p.y-points[i].y),0)/100*1000),facingLeft:destination==='desk',open};
  status.textContent=destination==='desk'?'走向电脑桌…':'走向门口…';
}
function showPanel(kind){
  panel.hidden=false;document.getElementById('feedback').textContent='';
  document.getElementById('panel-kicker').textContent=kind==='desk'?'工作电脑':'外出';
  document.getElementById('panel-title').textContent=kind==='desk'?'今天从哪件事开始？':'准备去哪里？';
  document.getElementById('panel-desc').textContent=kind==='desk'?'选择一项办公行动。':'目的地示意，正式游戏由当前章节解锁。';
  const options=document.getElementById('options');options.replaceChildren();
  for(const label of kind==='desk'?['整理卷宗','检索法条','查看来信','返回房间']:['律所公共区','法院','街区','留在房间']){
    const b=document.createElement('button');b.textContent=label;b.onclick=()=>{if(label==='返回房间'||label==='留在房间'){panel.hidden=true;return}document.getElementById('feedback').textContent=`已选择「${label}」。此处演示菜单，尚未连接正式任务或目标场景。`};options.append(b);
  }
}
function animate(now){
  if(!exportMode){
    if(current?.demo){const t=(now-current.start)/1000;const state=demoAt(t);player=pointAlong(route,state.progress);facingLeft=true;if(t>=8.2){player={...desk};current=null;status.textContent='已到电脑桌前。点击“办公”查看电脑选项。'}}
    else if(current){const p=Math.min(1,(now-current.start)/current.duration);player=pointAlong(current.points,p);facingLeft=current.facingLeft;draw(player,p<1?Math.floor((now-current.start)/125)%8:2,facingLeft);if(p===1){const open=current.open;current=null;status.textContent='已到达。';if(open)showPanel(open)}}
    else draw(player,2,facingLeft);
  }
  requestAnimationFrame(animate);
}
document.getElementById('replay').onclick=()=>{panel.hidden=true;current={demo:true,start:performance.now()};status.textContent='门口 → 电脑桌';};
for(const id of ['computer','desk-hotspot'])document.getElementById(id).onclick=()=>move('desk','desk');
for(const id of ['door','exit-hotspot'])document.getElementById(id).onclick=()=>move('door','door');
document.getElementById('close').onclick=()=>{panel.hidden=true};
window.addEventListener('keydown',e=>{if(e.key==='Escape')panel.hidden=true});

const prepare=new URLSearchParams(location.search).has('prepare');
const spritePath=prepare?'protagonist_walk_left_source_v01.png':'protagonist_walk_left_v01.png';
window.roomReady=Promise.all([image('../../../assets/art/daily/daily_room_warm_v02.png'),image('../../../assets/art/daily/characters/'+spritePath)]).then(([bg,source])=>{
  background=bg;
  if(prepare)sprites=extractFrames(source);
  else{atlas=source;for(let i=0;i<8;i++){const f=document.createElement('canvas');f.width=320;f.height=480;f.getContext('2d').drawImage(source,(i%4)*320,Math.floor(i/4)*480,320,480,0,0,320,480);sprites.push(f)}}
  draw(player);status.textContent='点击“播放进门动画”，或选择办公、外出。';
  window.roomDemo={drawAt:demoAt,atlas:()=>atlas.toDataURL('image/png'),snapshot:()=>canvas.toDataURL('image/png'),position:()=>player};
  requestAnimationFrame(animate);return true;
}).catch(error=>{status.textContent='素材载入失败，请使用本地预览服务器打开此页。';throw error});
