function FilterBar({
  startDate,
  endDate,
  selectedRegion,
  selectedProduct,
  regions,
  products,
  onStartDateChange,
  onEndDateChange,
  onRegionChange,
  onProductChange,
  onApplyFilters,
}) {
  return (
    <section style={{ marginBottom: "2rem" }}>
      <h2>Filters</h2>
      <div
        style={{
          display: "flex",
          gap: "1rem",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <div>
          <label htmlFor="start-date">Start Date</label>
          <br />
          <input
            id="start-date"
            type="date"
            value={startDate}
            onChange={(e) => onStartDateChange(e.target.value)}
          />
        </div>

        <div>
          <label htmlFor="end-date">End Date</label>
          <br />
          <input
            id="end-date"
            type="date"
            value={endDate}
            onChange={(e) => onEndDateChange(e.target.value)}
          />
        </div>

        <div>
          <label htmlFor="region-filter">Region</label>
          <br />
          <select
            id="region-filter"
            value={selectedRegion}
            onChange={(e) => onRegionChange(e.target.value)}
          >
            <option value="">All Regions</option>
            {regions.map((region) => (
              <option key={region.id} value={region.id}>
                {region.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="product-filter">Product</label>
          <br />
          <select
            id="product-filter"
            value={selectedProduct}
            onChange={(e) => onProductChange(e.target.value)}
          >
            <option value="">All Products</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.name}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginTop: "1.4rem" }}>
          <button onClick={onApplyFilters}>Apply Filters</button>
        </div>
      </div>
    </section>
  );
}

export default FilterBar;