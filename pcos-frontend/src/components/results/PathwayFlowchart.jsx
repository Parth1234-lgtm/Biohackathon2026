function PathwayNode({ node, role, selected, onSelect }) {
  if (!node) return null;

  const isSelected = selected === node.name;
  const status = node.blood_status;

  return (
    <button
      type="button"
      onClick={() => onSelect(node)}
      className={`w-full max-w-xs rounded-2xl border-2 px-5 py-4 text-left transition-all duration-300 hover:-translate-y-1 hover:shadow-lg ${
        isSelected
          ? "border-burgundy bg-burgundy text-white shadow-xl"
          : "border-sand bg-white/90 text-text-dark hover:border-dusty-pink"
      }`}
    >
      <p className="font-display text-lg font-bold">{node.name}</p>
      {node.protein_name && (
        <p className={`mt-1 text-xs ${isSelected ? "text-white/80" : "text-text-light"}`}>
          {node.protein_name}
        </p>
      )}
      {node.role && (
        <p className={`mt-2 text-xs italic ${isSelected ? "text-white/70" : "text-text-light"}`}>
          {node.role}
        </p>
      )}
      {status && (
        <span
          className={`mt-3 inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase ${
            isSelected
              ? "bg-white/20 text-white"
              : status === "elevated"
                ? "bg-burgundy/10 text-burgundy"
                : "bg-sand/50 text-text-dark"
          }`}
        >
          {status}
        </span>
      )}
    </button>
  );
}

function Arrow() {
  return (
    <div className="flex justify-center py-2 text-burgundy/50">
      <svg width="24" height="32" viewBox="0 0 24 32" fill="currentColor">
        <path d="M12 0 L12 24 M6 18 L12 28 L18 18" stroke="currentColor" strokeWidth="2" fill="none" />
      </svg>
    </div>
  );
}

export default function PathwayFlowchart({ pathway_graph, selectedNode, onSelectNode }) {
  const { commander_tf, main_disease_node, soldier_nodes } = pathway_graph ?? {};

  return (
    <section className="glass-card mb-8 rounded-2xl p-8">
      <h3 className="mb-6 font-display text-xl font-semibold text-burgundy">Pathway Network</h3>
      <p className="mb-6 text-sm text-text-light">
        Click any node to load its 3D protein structure below
      </p>

      <div className="flex flex-col items-center">
        {commander_tf && (
          <>
            <PathwayNode
              node={commander_tf}
              selected={selectedNode?.name}
              onSelect={onSelectNode}
            />
            <Arrow />
          </>
        )}

        {main_disease_node && (
          <>
            <PathwayNode
              node={main_disease_node}
              selected={selectedNode?.name}
              onSelect={onSelectNode}
            />
            <Arrow />
          </>
        )}

        {soldier_nodes?.length > 0 && (
          <div className="grid w-full max-w-3xl gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {soldier_nodes.map((node) => (
              <PathwayNode
                key={node.name}
                node={node}
                selected={selectedNode?.name}
                onSelect={onSelectNode}
              />
            ))}
          </div>
        )}

        {!commander_tf && !main_disease_node && !soldier_nodes?.length && (
          <p className="text-text-light">No pathway data available.</p>
        )}
      </div>
    </section>
  );
}
