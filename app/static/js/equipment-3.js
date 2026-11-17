(function(){
    const modal=document.getElementById('alternativeInspectorModal');
    const content=document.getElementById('alternativeInspectorContent');
    const close=document.getElementById('alternativeInspectorClose');
    window.openAlternativeInspector=async function(id){
        try{
            const r=await fetch('/api/equipment/'+id,{cache:'no-store'});
            if(!r.ok) return;
            const d=await r.json();
            const photo=d.equipment_photo_url||d.location_photo_url||'';
            content.innerHTML=`
                <div class="alternative-inspector-head"><div><span class="equipment-inspector-code">${escapeHtmlAlt(d.code||'—')}</span><h2>${escapeHtmlAlt(d.description||'—')}</h2><p>${escapeHtmlAlt([d.manufacturer,d.model].filter(Boolean).join(' · '))}</p></div><span class="status">${escapeHtmlAlt(d.status||'—')}</span></div>
                ${photo?`<img class="alternative-inspector-photo" src="${photo}" alt="">`:''}
                <dl class="equipment-inspector-grid">
                    <div><dt>Αρ. Μητρώου ΔΕΗ</dt><dd>${escapeHtmlAlt(d.dei_registry_number||'—')}</dd></div>
                    <div><dt>Κωδικός ΤΕΜ</dt><dd>${escapeHtmlAlt(d.tem_internal_code||'—')}</dd></div>
                    <div><dt>Serial Number</dt><dd>${escapeHtmlAlt(d.serial_number||'—')}</dd></div>
                    <div><dt>Θέση</dt><dd>${escapeHtmlAlt(d.location||'—')}</dd></div>
                </dl>
                <a class="primary-button" href="/equipment/${encodeURIComponent(d.id)}">Άνοιγμα πλήρους καρτέλας</a>`;
            modal.classList.add('is-open'); modal.setAttribute('aria-hidden','false');
        }catch(e){console.error(e);}
    };
    function escapeHtmlAlt(v){const x=document.createElement('div');x.textContent=String(v||'');return x.innerHTML;}
    function shut(){modal.classList.remove('is-open');modal.setAttribute('aria-hidden','true');}
    close.addEventListener('click',shut); modal.addEventListener('click',e=>{if(e.target===modal)shut();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape')shut();});
})();
