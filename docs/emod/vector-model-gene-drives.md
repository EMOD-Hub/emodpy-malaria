# Gene Drives


Existing malaria control tools — insecticide-treated nets, indoor residual spraying, and
antimalarial drugs — have driven significant reductions in transmission, but the spread of
insecticide and drug resistance threatens to erode these gains. Reaching elimination in
high-transmission settings will likely require new tools that can self-propagate through wild
mosquito populations without continuous mass releases.

Gene drives are genetic elements that bias their own inheritance beyond what Mendelian
genetics predicts. In a standard heterozygote, a transgene has a 50% chance of being passed
to each offspring and is likely lost over time if it carries any fitness cost. A gene drive
overcomes this: most or all offspring of a heterozygous carrier inherit the drive element,
allowing it to spread rapidly to high frequency within a population over just a few generations
(Figure 1).

![Figure 1. Mendelian inheritance (top) versus gene drive inheritance (bottom). Under Mendelian inheritance, a modified mosquito (red) mated with a wild mosquito (blue) produces 50% modified offspring, so the modification stays rare or is lost. A gene drive causes most or all offspring to inherit the drive element, enabling rapid population-wide spread. From Hammond and Galizi (2017), [doi:10.1080/20477724.2018.1438880](https://doi.org/10.1080/20477724.2018.1438880).](../images/vector-genetics/mendelian-vs-gene-drive.png)
*Figure 1. Mendelian inheritance (top) versus gene drive inheritance (bottom). Under Mendelian inheritance, a modified mosquito (red) mated with a wild mosquito (blue) produces 50% modified offspring, so the modification stays rare or is lost. A gene drive causes most or all offspring to inherit the drive element, enabling rapid population-wide spread. From Hammond and Galizi (2017), [doi:10.1080/20477724.2018.1438880](https://doi.org/10.1080/20477724.2018.1438880).*

Two broad strategies have been proposed for gene-drive-based malaria control (Figure 2).
**Population suppression** drives are designed to reduce mosquito reproductive capacity —
for example, by distorting the sex ratio toward males — eventually reducing the population
below the threshold required to sustain transmission. **Population replacement** drives spread
a refractory trait (inability to transmit malaria) through the population, leaving mosquito
numbers intact but eliminating their capacity to transmit disease.

![Figure 2. Population suppression (left) reduces the total vector population over time. Population replacement (right) maintains population size but converts wild mosquitoes (blue) to modified, malaria-refractory mosquitoes (red). From Hammond and Galizi (2017), [doi:10.1080/20477724.2018.1438880](https://doi.org/10.1080/20477724.2018.1438880).](../images/vector-genetics/suppression-vs-replacement.png)
*Figure 2. Population suppression (left) reduces the total vector population over time. Population replacement (right) maintains population size but converts wild mosquitoes (blue) to modified, malaria-refractory mosquitoes (red). From Hammond and Galizi (2017), [doi:10.1080/20477724.2018.1438880](https://doi.org/10.1080/20477724.2018.1438880).*

A further distinction is between **self-sustaining** drives, which are designed to spread
indefinitely once released, and **self-limiting** drives, which are engineered to dissipate
over time — an important consideration for ecological containment and regulatory approval.

EMOD supports five gene drive types that model these different strategies. Gene drives
are configured in the `Drivers` array within each species entry in `Vector_Species_Params`.

!!! note
    The model does not allow for mixing drive types within a species.

## CLASSIC


The classic gene drive bundles a Cas9 endonuclease and a guide RNA (gRNA) at the same locus as
the drive allele (represented by `Driving_Allele`). When two gametes come together during
genome formation, if one gamete has the driving allele and the other has the target allele
(`Allele_To_Replace`), the drive cuts the target and copies the driving allele into the cut
site.

The drive requires all of the following conditions to be met:

- The `Driving_Allele` must be present in exactly one of the two gametes (not both).
- The `Allele_To_Replace` for the driving allele must exist in the other gamete.
- The copy of the driving allele itself must succeed (based on `Copy_To_Likelihood`).

If any of these conditions is not met, the entire drive fails and standard Mendelian inheritance
applies. When driving additional loci (effectors), the `Allele_To_Copy` must exist in the
gamete with the driving allele, and the `Allele_To_Replace` must exist in the other gamete.

When the conversion is not perfect, you can configure the drive to model different outcomes
at the cut site:

- **Successful copy**: The drive allele is copied (super-Mendelian inheritance).
- **Resistance allele**: Non-homologous end joining (NHEJ) creates a resistant allele that can no
  longer be cut, preventing future drive conversion at that locus.
- **No change**: The cut fails entirely.

![Classic gene drive system. A drive mosquito mates with a wild-type mosquito; in the offspring germline, the Cas9 and gRNA cut the wild-type chromosome at the target site and homology-directed repair copies the complete construct. Possible alleles in offspring: wild type (no copy), complete construct (successful copy), or resistant (non-homologous end joining creates a mutated target site the drive can no longer recognize). From Leung et al. (2022), [doi:10.1186/s12936-022-04242-2](https://doi.org/10.1186/s12936-022-04242-2).](../images/vector-genetics/classic-gene-drive.png)
*Classic gene drive system. A drive mosquito mates with a wild-type mosquito; in the offspring germline, the Cas9 and gRNA cut the wild-type chromosome at the target site and homology-directed repair copies the complete construct. Possible alleles in offspring: wild type (no copy), complete construct (successful copy), or resistant (non-homologous end joining creates a mutated target site the drive can no longer recognize). From Leung et al. (2022), [doi:10.1186/s12936-022-04242-2](https://doi.org/10.1186/s12936-022-04242-2).*

### Example configuration

A classic drive at a single locus. The `drive_a` allele bundles Cas9 + gRNA and copies itself
over the wild-type allele `wild_a` with 95% efficiency. The remaining 5% produce a resistance
allele through NHEJ:

[link](../json/vector-model-gene-drives-1.json)


## INTEGRAL_AUTONOMOUS


The integral autonomous drive separates the Cas9 (driver) and gRNA (effector) onto different
loci. Unlike the classic drive, it can drive the effector even when the driver allele itself
fails to copy. It can copy an effector allele from either gamete into the other, since the Cas9 produced
by the driver acts across gametes regardless of which gamete carries the driver.

The drive activates whenever at least one copy of the driver allele is present in the genome —
it does not require heterozygosity at the driven locus. For each driven locus, the
`Allele_To_Copy` must exist in the gamete with the driving allele, and the
`Allele_To_Replace` must exist in the other gamete. If one of these conditions is not met for
a particular locus, nothing happens at that locus, but other loci can still be driven.

![Integral gene drive system. Driver and effector are on separate loci, each with their own gRNA, allowing each to be copied independently. Possible alleles at each locus: wild type, the introduced construct, resistant (drive can no longer recognize the target site), or loss-of-function (lethal mutation at an essential gene target site). From Leung et al. (2022), [doi:10.1186/s12936-022-04242-2](https://doi.org/10.1186/s12936-022-04242-2).](../images/vector-genetics/integral-gene-drive.png)
*Integral gene drive system. Driver and effector are on separate loci, each with their own gRNA, allowing each to be copied independently. Possible alleles at each locus: wild type, the introduced construct, resistant (drive can no longer recognize the target site), or loss-of-function (lethal mutation at an essential gene target site). From Leung et al. (2022), [doi:10.1186/s12936-022-04242-2](https://doi.org/10.1186/s12936-022-04242-2).*

### Example configuration

An autonomous drive with one driver locus (`a1`) and one effector locus (`b1`). The driver
`a1` copies itself over `a0` with 90% efficiency and also drives the effector `b1` over
`b0` at 90%. Because the driver and effector are at separate loci, the effector can be driven
even if the driver allele itself fails to copy, and vice versa (the driver can be driven
even if the effector fails to copy):

[link](../json/vector-model-gene-drives-2.json)

## DAISY_CHAIN


A daisy chain drive is a multi-element system where each component drives the next in a chain,
but the first element in the chain has no drive acting on it. This creates a self-limiting drive:
the first element is lost from the population through standard Mendelian dilution, which
eventually removes the driving force from downstream elements. Daisy chain drives are modeled as
a variant of the autonomous drive with specific locus dependencies.

![Daisy chain drive. (a) CRISPR components are separated so each element drives the next: C drives B, B drives A. C is not driven and is lost in half of offspring; once C is gone, B loses its driver and is lost in turn, continuing until the drive stops. (b) The loss of non-driving elements is analogous to gravity on a rocket — adding more elements allows the system to spread further before it runs out of genetic fuel. From Esvelt and Gemmell (2017), [doi:10.1371/journal.pbio.2003850](https://doi.org/10.1371/journal.pbio.2003850).](../images/vector-genetics/daisy-chain.png)
*Daisy chain drive. (a) CRISPR components are separated so each element drives the next: C drives B, B drives A. C is not driven and is lost in half of offspring; once C is gone, B loses its driver and is lost in turn, continuing until the drive stops. (b) The loss of non-driving elements is analogous to gravity on a rocket — adding more elements allows the system to spread further before it runs out of genetic fuel. From Esvelt and Gemmell (2017), [doi:10.1371/journal.pbio.2003850](https://doi.org/10.1371/journal.pbio.2003850).*

### Example configuration

A two-element daisy chain. `Ct` (at the end of the chain) drives `Bt` into the population.
`Bt` (in the middle) drives `At`, the effector. Nothing drives `Ct` itself, so it is lost
through Mendelian dilution over time, making the drive self-limiting.

!!! note
    Because DAISY_CHAIN is implemented as a variant of INTEGRAL_AUTONOMOUS, `Alleles_Driven`
    must include an entry for the driver allele's own locus. This entry defines what happens
    at that locus when the drive is active. For a daisy element that does not drive itself,
    set the `Copy_To_Likelihood` for that entry to 100% failure (`Likelihood: 1.0` for
    the `Allele_To_Replace`), as shown below for `Bt` and `Ct`.

[link](../json/vector-model-gene-drives-3.json)

## X_SHRED and Y_SHRED


Sex-ratio distortion drives work by destroying (shredding) sex-chromosome-bearing gametes during
spermatogenesis. These drives only apply to gametes created from a male genome and are configured
via the `Shredding_Alleles` parameter block rather than `Alleles_Driven`.

- **X_SHRED**: Destroys X-bearing sperm, biasing offspring toward males. Requires the male
  parent to carry the driving allele (`Allele_Required`) on the Y chromosome.
- **Y_SHRED**: Destroys Y-bearing sperm, biasing offspring toward females. Requires the male
  parent to carry the driving allele (`Allele_Required`) on the X chromosome.

Each shredding drive specifies:

- `Allele_Required` — the allele the male must carry for shredding to occur
- `Allele_To_Shred` — the sex-chromosome allele that is targeted for destruction
- `Allele_To_Shred_To` — the allele that surviving shredded gametes are converted to
- `Allele_Shredding_Fraction` — the fraction of targeted gametes destroyed (0.0--1.0, default
  1.0)
- `Allele_To_Shred_To_Surviving_Fraction` — the fraction of shredded gametes that survive as
  the `Allele_To_Shred_To` allele rather than being eliminated (0.0--1.0, default 0.0)

![X-shredding (top) and Y-shredding (bottom) during male meiosis. In X-shredding, an endonuclease (I-PpoI) damages X-bearing sperm during meiotic division, leaving primarily Y-bearing sperm viable and producing approximately 95% male-biased offspring. In Y-shredding, a Cas9/gRNA construct targets and damages Y-bearing sperm, leaving primarily X-bearing sperm viable and producing approximately 99% female-biased offspring. From Vitale, M. (2024), Target Malaria, [Y-chromosome shredding in Anopheles gambiae](https://targetmalaria.org/latest/blog/y-chromosome-shredding-in-anopheles-gambiae-a-new-genetic-sexing-strain-reveals-novel-insight-into-the-biology-of-synthetic-sex-ratio-distorters/).](../images/vector-genetics/x-shred-y-shred-gene-drive.png)
*X-shredding (top) and Y-shredding (bottom) during male meiosis. In X-shredding, an endonuclease (I-PpoI) damages X-bearing sperm during meiotic division, leaving primarily Y-bearing sperm viable and producing approximately 95% male-biased offspring. In Y-shredding, a Cas9/gRNA construct targets and damages Y-bearing sperm, leaving primarily X-bearing sperm viable and producing approximately 99% female-biased offspring. From Vitale, M. (2024), Target Malaria, [Y-chromosome shredding in Anopheles gambiae](https://targetmalaria.org/latest/blog/y-chromosome-shredding-in-anopheles-gambiae-a-new-genetic-sexing-strain-reveals-novel-insight-into-the-biology-of-synthetic-sex-ratio-distorters/).*

### Example configuration


An X-shredding drive that biases offspring toward males. The drive allele `Ad` is at a
non-gender locus. When a male carrying `Ad` also has the Y-chromosome allele `Yw`
(`Allele_Required`), his X-bearing sperm carrying `Xw` (`Allele_To_Shred`) are destroyed.
`Driving_Allele_Params` specifies how the drive allele itself is inherited:

[link](../json/vector-model-gene-drives-4.json)

With `Allele_Shredding_Fraction` = 1.0 and `Allele_To_Shred_To_Surviving_Fraction` = 0.0,
all X-bearing sperm are destroyed and none survive as the `Xm` allele.

**Y_SHRED example**:

A Y-shredding drive that biases offspring toward females. When a male carrying `Ad` also has
the X-chromosome allele `Xw` (`Allele_Required`), his Y-bearing sperm carrying `Yw`
(`Allele_To_Shred`) are destroyed:

[link](../json/vector-model-gene-drives-5.json)

## Configuration parameters


Gene drivers are defined in the `Drivers` array within each species entry in
`Vector_Species_Params`. The following table lists all parameters. Parameters marked as applying
to specific driver types are ignored for other types.

{{ read_csv("csv/config-gene-drives.csv") }}
