function processdiffs(indx, files) {
    file  = files[indx]
    dictJson[file] = []
    for (var i=0; i<files.length; i++) {
      if (indx === i)
        continue
      //console.log(file + " <-> " + files[i])
      f1_length = ASTS[file].length
      if (!(files[i] in ASTS)) {
        console.log("ERROR: missing AST for file " +files[i])
        return
      }
      f2_length = ASTS[files[i]].length
    
      /*if (f1_length < f2_length) {
        if( (f1_length/f2_length) < LENGTH_RATIO) { 
          ratio = calc_ratio(file, files[i]);
          console.log(file + " <-> " + files[i] + ": " + ratio + " size_ratio: "+(f1_length/f2_length));
        }
      }*/
      ratio = calc_ratio(file, files[i]);
      var v = files[i]
      console.log(file, files[i], ratio)
      var b = {}
      b[files[i]]=ratio;
        
      dictJson[file].push(b)
      // console.log(file + " <-> " + files[i] + ": simlarity: " + ratio + " size_ratio: "+(f1_length/f2_length));  
    }
    
  }
  
  function calc_ratio(f1, f2) {
    // ASTS = global.ASTS;
    s = new difflib.SequenceMatcher(null, ASTS[f1], ASTS[f2]);
    qr = s.quickRatio();
    if (qr < 0.1) return qr;
    blocks = s.getMatchingBlocks();
    size = 0.0;
    for (var i=0; i<blocks.length; i++) {
      size += blocks[i][2]
    }
    console.log(size,ASTS[f1].length,ASTS[f2].length)
  //   return size/Math.min(ASTS[f1].length,ASTS[f2].length);
    return size/ASTS[f1].length;
      
  }
  
  function analyzeCode(code) {
    try {
      var ast = esprima.parseScript(code);
    } catch (err) {
      // if esprima cannot parse the script, ignore it.
      var ast = []
    }
    var astt = []
    traverse(ast, function(node) {
      //console.log(node.type);
      if (node != null)
        astt.push(node.type);
    });
    //console.log(astt)
    return astt;
  }
  
  function traverse(node, func) {
    func(node);
    for (var key in node) { 
      if (node.hasOwnProperty(key)) { 
        var child = node[key];
        if (typeof child === 'object' && child !== null) { 
          if (Array.isArray(child)) {
            child.forEach(function(node) { 
              traverse(node, func);
            });
          } else {
            traverse(child, func); 
          }
        }
      }
    }
  }
  
  
  function h(code) {
    const code_sha256 = crypto.createHmac('sha256', code).digest('hex');
    console.log(code_sha256)
    if (scripts.hasOwnProperty(code_sha256)) { 
      console.log(scripts[code_sha256])
    }
  }