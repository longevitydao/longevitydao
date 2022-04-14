import { expect } from "chai";
// import { BigNumber, ContractReceipt, ContractTransaction } from "ethers";
import { ethers } from "hardhat";

async function getDeployedVotingContract(proposals: string[]): Promise<any> {
  const VotingContractFactory = await ethers.getContractFactory(
    "VotingContract"
  );
  const votingContract = await VotingContractFactory.deploy(proposals);
  await votingContract.deployed();
  return votingContract;
}

describe("VotingContract", function () {
  it("Voting works correctly.", async function () {
    const votingContract = await getDeployedVotingContract(["Prop1", "Prop2"]);

    await votingContract.vote("Prop1");

    expect(await votingContract.votes("Prop1")).to.equal(1000);
    expect(await votingContract.votes("Prop2")).to.equal(0);
  });

  it("Can't vote on invalid proposal.", async function () {
    const votingContract = await getDeployedVotingContract(["Prop1", "Prop2"]);

    await expect(votingContract.vote("Prop3")).to.be.revertedWith(
      "Invalid proposal."
    );
  });

  it("Multiple voting works correctly.", async function () {
    const votingContract = await getDeployedVotingContract(["Prop1", "Prop2"]);

    await votingContract.vote("Prop1");
    await votingContract.vote("Prop2");
    await votingContract.vote("Prop2");
    await votingContract.vote("Prop1");
    await votingContract.vote("Prop1");

    expect(await votingContract.votes("Prop1")).to.equal(3000);
    expect(await votingContract.votes("Prop2")).to.equal(2000);
  });

  it("Events are emitted.", async function () {
    const votingContract = await getDeployedVotingContract(["Prop1", "Prop2"]);

    await expect(votingContract.vote("Prop1"))
      .to.emit(votingContract, "VoteCountsUpdated")
      .withArgs("Prop1", 1000);

    await expect(votingContract.vote("Prop1"))
      .to.emit(votingContract, "VoteCountsUpdated")
      .withArgs("Prop1", 2000);
  });

  it("Failure if you send eth directly to the contract.", async function () {
    const votingContract = await getDeployedVotingContract(["Prop1", "Prop2"]);
    const [owner] = await ethers.getSigners();

    // Deposit eth.
    await expect(
      owner.sendTransaction({
        to: votingContract.address,
        value: ethers.utils.parseEther("1.0"),
      })
    ).to.be.revertedWith("");
  });
});
